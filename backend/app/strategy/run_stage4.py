import os
import pandas as pd
from datetime import datetime
import ccxt
import requests

from app.strategy.ema_rsi_stage2 import ema_rsi_strategy


# -----------------------------
# CONFIGURATION
# -----------------------------
SYMBOLS = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "XRP/USDT", "SOL/USDT"]
TIMEFRAMES = ["5m", "15m", "1h", "12h"]
BACKEND_URL = os.getenv("BACKEND_SIGNAL_UPDATE_URL")   # <-- FIXED (env variable)
LIMIT_CANDLES = 300


# -----------------------------
# FETCH LIVE MARKET DATA
# -----------------------------
def fetch_live_data(symbol, timeframe):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=LIMIT_CANDLES)

    df = pd.DataFrame(ohlcv, columns=["ts", "open", "high", "low", "close", "volume"])
    df["ts"] = pd.to_datetime(df["ts"], unit='ms')
    df[["open","high","low","close","volume"]] = df[["open","high","low","close","volume"]].astype(float)
    return df


# -----------------------------
# GENERATE SIGNALS FOR ONE RUN
# -----------------------------
def generate_signals_once():

    live_signals = []

    for sym in SYMBOLS:
        for tf in TIMEFRAMES:
            try:
                df = fetch_live_data(sym, tf)
            except Exception as e:
                print(f"⚠ Error fetching {sym} {tf}: {e}")
                continue

            sig = ema_rsi_strategy(df, len(df) - 1)
            if sig is None:
                continue

            side, sl, tp = sig
            entry = float(df["close"].iloc[-1])

            signal = {
                "symbol": sym,
                "timeframe": tf,
                "side": side.upper(),
                "entry": round(entry, 6),
                "sl": round(sl, 6),
                "tp": round(tp, 6),
                "timestamp": datetime.now().isoformat()
            }

            live_signals.append(signal)

    return live_signals


# -----------------------------
# SEND SIGNALS TO BACKEND
# -----------------------------
def upload_to_backend(signals):
    if not BACKEND_URL:
        return {"status": "error", "message": "BACKEND_SIGNAL_UPDATE_URL not set"}

    try:
        resp = requests.post(BACKEND_URL, json=signals)
        resp.raise_for_status()
        return {"status": "uploaded", "count": len(signals)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# -----------------------------
# MAIN FUNCTION (Manual Trigger)
# -----------------------------
def run_strategy_once():
    print("\n🚀 Running strategy manually...")

    signals = generate_signals_once()

    upload_result = upload_to_backend(signals)

    return {
        "generated_signals": len(signals),
        "upload_status": upload_result,
        "signals": signals
    }


# Safe entry point (for local use only)
if __name__ == "__main__":
    print(run_strategy_once())
