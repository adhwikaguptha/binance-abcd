# app/services/strategy_engine.py

import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.ohlcv import OHLCV
from app.models.singal_bd import Signal, SignalStatus  # ✅ check filename spelling


def generate_signal_from_ohlcv(
    db: Session, symbol: str, timeframe: str, lookback: int = 300, force: bool = False
):
    """
    Generate a trading signal from OHLCV data.

    Strategy:
    - BUY when EMA50 crosses above EMA200
    - SELL when EMA50 crosses below EMA200
    - RSI added to ctx_json for extra info

    Args:
        db (Session): SQLAlchemy session
        symbol (str): Trading symbol (e.g. ETHUSDT)
        timeframe (str): Candle timeframe (e.g. 1h)
        lookback (int): Number of candles to check
        force (bool): If True, always generate a test BUY signal

    Returns:
        Signal | None
    """
    # Fetch OHLCV rows
    rows = (
        db.query(OHLCV)
        .filter_by(symbol=symbol, timeframe=timeframe)
        .order_by(OHLCV.ts.desc())
        .limit(lookback)
        .all()
    )

    # Require at least 200 candles, unless forcing
    if len(rows) < 200:
        if not force:
            return None

    # Convert to DataFrame
    df = pd.DataFrame(
        [
            {
                "ts": r.ts,
                "open": float(r.open),
                "high": float(r.high),
                "low": float(r.low),
                "close": float(r.close),
                "volume": float(r.volume),
            }
            for r in rows
        ]
    ).sort_values("ts")

    # Indicators
    if not df.empty:
        df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
        df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()
        delta = df["close"].diff()
        up = delta.clip(lower=0).rolling(14).mean()
        down = -delta.clip(upper=0).rolling(14).mean()
        rs = up / down
        df["rsi"] = 100 - (100 / (1 + rs))

        last, prev = df.iloc[-1], df.iloc[-2] if len(df) > 1 else (df.iloc[-1], df.iloc[-1])
    else:
        return None

    signal_data = None

    if force:
        # ⚡ Always generate a BUY for testing (ignores strategy logic)
        signal_data = {
            "side": "BUY",
            "entry": float(last["close"]),
            "sl": float(last["close"] * 0.99),
            "tp": float(last["close"] * 1.02),
        }
    else:
        # --- EMA crossover strategy ---
        if prev["ema50"] <= prev["ema200"] and last["ema50"] > last["ema200"]:
            signal_data = {
                "side": "BUY",
                "entry": float(last["close"]),
                "sl": float(last["close"] * 0.99),
                "tp": float(last["close"] * 1.02),
            }
        elif prev["ema50"] >= prev["ema200"] and last["ema50"] < last["ema200"]:
            signal_data = {
                "side": "SELL",
                "entry": float(last["close"]),
                "sl": float(last["close"] * 1.01),
                "tp": float(last["close"] * 0.98),
            }

    if signal_data:
        sig = Signal(
            strategy_id=None,
            symbol=symbol,
            side=signal_data["side"],
            entry=signal_data["entry"],
            sl=signal_data["sl"],
            tp=signal_data["tp"],
            qty=1.0,
            ttl_sec=86400,
            ctx_json=str(
                {
                    "ema50": float(last.get("ema50", 0)),
                    "ema200": float(last.get("ema200", 0)),
                    "rsi": float(last.get("rsi", 0)),
                }
            ),
            status=SignalStatus.pending,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=3600),
        )
        db.add(sig)
        db.commit()
        db.refresh(sig)
        return sig

    return None
