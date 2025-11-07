import csv
import io
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Union, TextIO
from sqlalchemy.orm import Session

from app.models.singal_bd import Signal, SignalStatus
from app.models.audit_log import AuditLog
from app.utils.helpers import safe_json_dumps


# ---------------- HELPER FUNCTIONS ----------------

def _parse_decimal(v):
    if v is None or v == "":
        return None
    try:
        return Decimal(str(v))
    except (InvalidOperation, ValueError):
        return None


def _parse_datetime(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass
    return None


def _row_hash(row: dict) -> str:
    keys = ["symbol", "side", "entry", "sl", "tp"]
    payload = "|".join(str(row.get(k, "")).strip() for k in keys)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------- MAIN INGEST FUNCTION ----------------

def ingest_suggestions(db: Session, file_or_path: Union[str, TextIO]) -> dict:
    """
    Ingest trading signals from CSV into DB.
    Supports both file paths and file-like objects.
    Returns summary: {inserted, updated, error_count, errors}
    """
    opened_here = False
    f = None

    # Handle both file paths and UploadFile objects
    if isinstance(file_or_path, str):
        f = open(file_or_path, mode="r", encoding="utf-8", newline="")
        opened_here = True
    else:
        if hasattr(file_or_path, "read"):
            file_or_path.seek(0)
            if isinstance(file_or_path.read(0), bytes):
                file_or_path.seek(0)
                f = io.TextIOWrapper(file_or_path, encoding="utf-8")
            else:
                f = file_or_path
        else:
            raise ValueError("file_or_path must be filename or file-like object")

    reader = csv.DictReader(f)
    # 🔥 Normalize all header names to lowercase for flexibility
    reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

    inserted = 0
    updated = 0
    errors = []
    new_signals = []

    try:
        for line_no, row in enumerate(reader, start=2):
            try:
                # Ensure all keys are lowercase
                row = {k.lower(): v for k, v in row.items()}

                symbol_raw = (row.get("symbol") or row.get("ticker") or "").strip()
                side_raw = (row.get("side") or "").strip().lower()
                entry = _parse_decimal(row.get("entry"))
                sl = _parse_decimal(row.get("sl") or row.get("stop_loss"))
                tp = _parse_decimal(row.get("tp") or row.get("take_profit"))
                qty = _parse_decimal(row.get("qty") or 0.01)
                ttl_sec = int(row.get("ttl_sec") or 300)
                signal_time = _parse_datetime(row.get("signal_time") or row.get("timestamp"))
                expires_at = _parse_datetime(row.get("expires_at"))
                external_id = (row.get("external_id") or row.get("id") or "").strip() or None

                # Validate and normalize
                if not symbol_raw or entry is None or sl is None:
                    raise ValueError("Missing required fields: symbol, entry, or sl")

                # Normalize symbol (BTC/USDT -> BTCUSDT)
                symbol = symbol_raw.replace("/", "").upper()

                # Normalize side to BUY/SELL
                if side_raw in ("buy", "long"):
                    side = "BUY"
                elif side_raw in ("sell", "short"):
                    side = "SELL"
                else:
                    raise ValueError(f"Invalid side '{side_raw}' — must be BUY or SELL")

                # Deduplication
                existing = None
                if external_id:
                    existing = db.query(Signal).filter(Signal.external_id == external_id).first()

                if not existing:
                    ph = _row_hash(row)
                    existing = db.query(Signal).filter(Signal.payload_hash == ph).first()

                if existing:
                    existing.tp = tp or existing.tp
                    existing.expires_at = expires_at or existing.expires_at
                    db.add(existing)
                    updated += 1
                else:
                    new_signal = Signal(
                        symbol=symbol,
                        side=side,
                        entry=entry,
                        sl=sl,
                        tp=tp,
                        qty=qty,
                        ttl_sec=ttl_sec,
                        status=SignalStatus.PENDING,
                        created_at=signal_time or datetime.utcnow(),
                        expires_at=expires_at or (datetime.utcnow() + timedelta(seconds=ttl_sec)),
                        payload_hash=_row_hash(row),
                        external_id=external_id,
                        source=row.get("source") or "csv-ingest",
                    )
                    new_signals.append(new_signal)
                    inserted += 1

            except Exception as e:
                errors.append({
                    "line": line_no,
                    "error": str(e),
                    "row": row
                })
    finally:
        if opened_here:
            f.close()

    # --- COMMIT NEW SIGNALS ---
    try:
        if new_signals:
            db.add_all(new_signals)
        db.commit()
        print(f"✅ Commit successful — inserted {inserted}, updated {updated}")
    except Exception as e:
        db.rollback()
        print("❌ Commit failed:", e)
        raise

    # --- AUDIT LOG ---
    try:
        payload = {"inserted": inserted, "updated": updated, "error_count": len(errors)}
        db.add(AuditLog(
            who="system",
            what="SIGNAL_BATCH_INGEST",
            payload_json=safe_json_dumps(payload)
        ))
        db.commit()
        print("🧾 Audit log created.")
    except Exception as e:
        db.rollback()
        print("⚠️ Audit log commit failed:", e)

    return {
        "status": "success" if not errors else "partial_success",
        "inserted": inserted,
        "updated": updated,
        "error_count": len(errors),
        "errors": errors[:5]  # return only first 5 for readability
    }
