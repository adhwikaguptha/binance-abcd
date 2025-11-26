import os
from datetime import datetime, timezone

import pandas as pd
import ccxt
import requests

# Try absolute import (when used inside backend)
try:
    from app.strategy.ema_rsi_stage2 import ema_rsi_strategy
except ImportError:
    # Fallback if run locally: python app/strategy/run_stage4.py
    from ema_rsi_stage2 import ema_rsi_strategy


# -----------------------------
# CONFIGURATION
# -----------------------------
SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "ADA/USDT",
    "XRP/USDT",
    "SOL/USDT",
]

TIMEFRAMES = ["5m", "15m", "1h", "12h"]
LIMIT_CANDLES = 300

# This must be set in Railway:
# BACKEND_SIGNAL_UPDATE_URL=https://binance-abcd-production.up.railway.app/signals/update_active
BACKEND_URL = os.getenv("BACKEND_SIGNAL_UPDATE_URL")


# -----------------------------
# FETCH LIVE MARKET DATA
# -----------------------------
def fetch_live_data(symbol: str, timeframe: str) -> pd.DataFrame:
    """
    Fetch OHLCV candles from Binance using ccxt and return as DataFrame.
    """
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=LIMIT_CANDLES)

    df = pd.DataFrame(
        ohlcv,
        columns=["ts", "open", "high", "low", "close", "volume"],
    )
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    df[["open", "high", "low", "close", "volume"]] = df[
        ["open", "high", "low", "close", "volume"]
    ].astype(float)
    return df


# -----------------------------
# GENERATE SIGNALS (ONE RUN)
# -----------------------------
def generate_signals_once():
    """
    Loop through all symbols + timeframes, run EMA+RSI strategy,
    and build a list of signal dicts in the format expected by
    /signals/update_active.
    """
    all_signals = []
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

    for sym in SYMBOLS:
        for tf in TIMEFRAMES:
            try:
                df = fetch_live_data(sym, tf)
            except Exception as e:
                print(f"⚠ Error fetching {sym} {tf}: {e}")
                continue

            # Use last candle index
            idx = len(df) - 1
            try:
                result = ema_rsi_strategy(df, idx)
            except Exception as e:
                print(f"⚠ Strategy error for {sym} {tf}: {e}")
                continue

            if result is None:
                continue

            side, sl, tp = result
            entry = float(df["close"].iloc[-1])

            # Build payload matching SignalCreate in signals.py
            signal_payload = {
                "symbol": sym,                          # e.g. "BTC/USDT"
                "side": side.upper(),                   # "LONG" / "SHORT"
                "entry": round(float(entry), 6),
                "sl": round(float(sl), 6),
                "tp": round(float(tp), 6),
                "qty": None,                            # let backend / approve decide
                "strategy_id": 2,                       # arbitrary strategy id
                "confidence": f"tf={tf}",               # store timeframe info here
                "generated_at": now_utc.isoformat(),    # UTC time
            }

            all_signals.append(signal_payload)

    print(f"✅ Generated {len(all_signals)} signals in this run")
    return all_signals


# -----------------------------
# UPLOAD TO BACKEND
# -----------------------------
def upload_to_backend(signals):
    """
    POST the batch to /signals/update_active via BACKEND_SIGNAL_UPDATE_URL.
    """
    if not BACKEND_URL:
        msg = "BACKEND_SIGNAL_UPDATE_URL not set in environment."
        print("❌", msg)
        return {"status": "error", "message": msg}

    if not signals:
        print("ℹ No signals to upload (empty list).")
        return {"status": "no_signals", "count": 0}

    try:
        print(f"📡 Uploading {len(signals)} signals to {BACKEND_URL} ...")
        resp = requests.post(BACKEND_URL, json=signals, timeout=30)
        print("🔁 Backend response code:", resp.status_code)
        print("🔁 Backend response body:", resp.text)

        resp.raise_for_status()
        data = resp.json()
        return {
            "status": "uploaded",
            "count": len(signals),
            "backend_response": data,
        }
    except Exception as e:
        print("❌ Error uploading to backend:", e)
        return {"status": "error", "message": str(e)}


# -----------------------------
# MAIN SINGLE-RUN ENTRYPOINT
# -----------------------------
def run_strategy_once():
    """
    Main function used by FastAPI endpoint /run-strategy.
    Generates signals once and pushes them to backend.
    """
    print("\n🚀 Running EMA+RSI Stage 4 strategy (single run)...")

    signals = generate_signals_once()
    upload_result = upload_to_backend(signals)

    summary = {
        "generated_signals": len(signals),
        "upload_status": upload_result,
        "signals": signals,
    }

    print("📊 Run summary:", summary)
    return summary


# For local debugging: python -m app.strategy.run_stage4  OR  python run_stage4.py
if _name_ == "_main_":
    out = run_strategy_once()
    print("\n=== LOCAL RUN COMPLETE ===")
    print(out)
