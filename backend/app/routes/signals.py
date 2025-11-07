from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
from decimal import Decimal
import json
import tempfile
import os
import uuid
import pandas as pd
import io 
from app.database import get_db
from app.schemas.signal import SignalOut
from app.dependencies import get_user_id
from app.models.singal_bd import Signal, SignalStatus
from app.models.audit_log import AuditLog
from app.models.risk_settings import RiskSettings
from app.models.daily_pnl import DailyPnl
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.position import Position
from app.utils.helpers import safe_json_dumps
from app.services.suggestion_ingest import ingest_suggestions
from app.auth import get_current_user
from app.services.strategy_engine import generate_signal_from_ohlcv

router = APIRouter(tags=["signals"])

# ---------------- GET ROUTES ----------------

@router.get("/signals", response_model=List[SignalOut])
async def get_all_signals(db: Session = Depends(get_db)):
    """Fetch all signals."""
    return db.query(Signal).order_by(Signal.created_at.desc()).all()


@router.get("/signals/pending", response_model=List[SignalOut])
async def get_pending_signals(user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    """Fetch only pending signals."""
    return (
        db.query(Signal)
        .filter(Signal.status == SignalStatus.PENDING)
        .order_by(Signal.created_at.desc())
        .all()
    )
    
from fastapi import HTTPException
from datetime import datetime
@router.post("/signals/import_file")
async def import_signals_from_uploaded_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    import pandas as pd
    import io
    from datetime import datetime
    from app.models.singal_bd import Signal  # ✅ use correct model file

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")

    imported = 0

    for _, row in df.iterrows():
        try:
            # ✅ Map only what’s relevant
            new_signal = Signal(
                symbol=row["symbol"],
                side=row["side"],
                entry=float(row["entry"]),
                sl=float(row["SL"]),
                tp=float(row["TP"]),
                status="pending",
                created_at=datetime.utcnow(),
                source="file_import"
            )

            db.add(new_signal)
            imported += 1

        except Exception as e:
            print(f"⚠️ Skipping row due to error: {e}")

    db.commit()
    return {"message": f"✅ Imported {imported} signals from uploaded CSV file"}

# ---------------- POST ROUTES ----------------

@router.post("/signals/{id}/approve")
async def approve_signal(
    id: int,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    from app.services.broker import BinanceBroker
    import requests

    # Fetch signal
    signal = db.query(Signal).filter(Signal.id == id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    if signal.status != SignalStatus.PENDING:
        raise HTTPException(status_code=400, detail="Signal not pending")

    # Convert side
    side = {"LONG": "BUY", "SHORT": "SELL"}.get(signal.side.upper(), signal.side.upper())
    if side not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail=f"Invalid side: {signal.side}")

    # Qty adjustments
    entry_price = float(signal.entry)
    qty = float(signal.qty or 0.001)
    MIN_NOTIONAL_USD = 10.0
    if entry_price * qty < MIN_NOTIONAL_USD:
        qty = round(MIN_NOTIONAL_USD / entry_price, 6)

    # ✅ Fetch Binance LOT_SIZE dynamically instead of hardcoding
    try:
        symbol = signal.symbol.replace("/", "")
        exchange_info = requests.get("https://api.binance.com/api/v3/exchangeInfo").json()
        symbol_info = next((s for s in exchange_info["symbols"] if s["symbol"] == symbol), None)

        if not symbol_info:
            raise HTTPException(status_code=400, detail=f"Symbol {symbol} not found on Binance")

        lot_filter = next(f for f in symbol_info["filters"] if f["filterType"] == "LOT_SIZE")
        min_qty = float(lot_filter["minQty"])
        step_size = float(lot_filter["stepSize"])

        # Apply Binance limits
        qty = max(qty, min_qty)
        qty = (qty // step_size) * step_size
        qty = round(qty, 6)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch Binance filters: {e}")

    broker = BinanceBroker(db)

    try:
        # Place order on Binance
        order_data = {"symbol": signal.symbol, "side": side, "qty": qty, "entry": entry_price}
        result = await broker.place_order(user_id, order_data)
        if not result or not result.get("orderId"):
            raise Exception("Binance rejected order")

        # Insert order in DB
        order = Order(
            user_id=user_id,
            signal_id=signal.id,
            side=side,
            qty=qty,
            price=result.get("price", entry_price),
            sl=signal.sl,
            tp=signal.tp,
            binance_order_id=result.get("orderId"),
            status=OrderStatus.FILLED if result.get("status") == "FILLED" else OrderStatus.NEW,
            ts=datetime.utcnow(),
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        # Create position immediately as OPEN
        position = Position(
            user_id=user_id,
            order_id=order.id,
            symbol=signal.symbol,
            side=side,
            qty=qty,
            avg_price=order.price,
            sl=signal.sl,
            tp=signal.tp,
            status="OPEN",
            opened_at=datetime.utcnow(),
        )
        db.add(position)
        db.commit()
        db.refresh(position)
        print(f"📌 Position {position.id} created as OPEN in DB")

        # Update signal
        signal.status = SignalStatus.APPROVED
        signal.approved_by = user_id
        signal.approved_at = datetime.utcnow()
        db.commit()

        print(f"✅ Order placed for {signal.symbol} | Binance ID: {result.get('orderId')}")
        return {
            "status": "success",
            "order_id": order.id,
            "binance_order_id": result.get("orderId"),
            "position_id": position.id,
        }

    except Exception as e:
        db.rollback()
        signal.status = SignalStatus.REJECTED
        signal.rejected_by = user_id
        signal.rejected_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=502, detail=f"Broker error: {str(e)}")


# ✅ Reject Signal
@router.post("/signals/{id}/reject")
async def reject_signal(
    id: int,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Reject a pending or active signal (cancel Binance order if placed)."""
    from app.services.broker import BinanceBroker

    signal = db.query(Signal).filter(Signal.id == id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    if signal.status not in [SignalStatus.PENDING, SignalStatus.APPROVED]:
        raise HTTPException(status_code=400, detail="Signal cannot be rejected")

    order = db.query(Order).filter(Order.signal_id == id).first()
    if order and order.binance_order_id:
        broker = BinanceBroker(db)
        cancel_result = await broker.cancel_order(user_id, order.binance_order_id)
        order.status = OrderStatus.CANCELED
        db.commit()
    else:
        cancel_result = {"message": "No Binance order to cancel"}

    signal.status = SignalStatus.REJECTED
    signal.rejected_by = user_id
    signal.rejected_at = datetime.utcnow()
    db.commit()

    db.add(AuditLog(
        who=str(user_id),
        what="SIGNAL_REJECTED",
        payload_json=safe_json_dumps({
            "signal_id": signal.id,
            "cancel_result": cancel_result,
            "timestamp": datetime.utcnow().isoformat()
        })
    ))
    db.commit()

    return {
        "status": "success",
        "message": f"Signal {signal.id} rejected successfully.",
        "cancel_result": cancel_result
    }


# ✅ Stage 4 integration — replace active signals each cycle
from pydantic import BaseModel

class SignalCreate(BaseModel):
    symbol: str
    side: str
    entry: float
    sl: float
    tp: float | None = None
    qty: float | None = None
    strategy_id: int | None = None
    confidence: str | None = None
    generated_at: datetime | None = None


@router.post("/signals/update_active")
def update_active_signals(signals: List[SignalCreate], db: Session = Depends(get_db)):
    """Soft delete old + insert new batch."""
    db.query(Signal).filter(Signal.active == True).update({"active": False})
    db.commit()

    batch_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    for s in signals:
        sig = Signal(
            symbol=s.symbol,
            side=s.side,
            entry=s.entry,
            sl=s.sl,
            tp=s.tp,
            qty=s.qty,
            strategy_id=s.strategy_id,
            status=SignalStatus.PENDING,
            created_at=s.generated_at or datetime.utcnow(),
            ts=datetime.utcnow(),
            active=True,
            batch_id=batch_id,
            source="auto"
        )
        db.add(sig)

    db.commit()
    return {"status": "ok", "inserted": len(signals), "batch_id": batch_id}


@router.get("/signals/active", response_model=List[SignalOut])
async def get_active_signals(db: Session = Depends(get_db)):
    """Return active signals only."""
    return (
        db.query(Signal)
        .filter(Signal.active == True)
        .order_by(Signal.created_at.desc())
        .all()
    )
