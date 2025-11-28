import os
from datetime import datetime, timezone
import pandas as pd
import ccxt
import requests

import json

BACKEND_SIGNAL_UPDATE_URL = os.getenv("BACKEND_SIGNAL_UPDATE_URL")


# Try absolute import (when used inside FastAPI)
try:
    from app.strategy.ema_rsi_stage2 import ema_rsi_strategy
except ImportError:
    # Local debug fallback
    from ema_rsi_stage2 import ema_rsi_strategy


# ================================
# CONFIG
# ================================
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

# Set this in Railway:
# BACKEND_SIGNAL_UPDATE_URL=https://your-domain/signals/update_active
BACKEND_URL = os.getenv("BACKEND_SIGNAL_UPDATE_URL")


# ================================
# FETCH LIVE OHLCV (TESTNET)
# ================================
def fetch_live_data(symbol: str, timeframe: str) -> pd.DataFrame:
    """
    Fetch OHLCV from Binance Testnet (unrestricted).
    Railway servers get BLOCKED by Binance.com,
    so we must use TESTNET.
    """
    try:
        exchange = ccxt.binance({
            "enableRateLimit": True
        })
        exchange.set_sandbox_mode(True)   # 🔥 SWITCH TO TESTNET

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

    except Exception as e:
        print(f"⚠ Failed to fetch {symbol} ({timeframe}): {e}")
        return None


# ================================
# GENERATE SIGNALS (ONE RUN)
# ================================
def generate_signals_once():
    print("\n🚀 Running EMA+RSI strategy once...")

    all_signals = []
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

    for sym in SYMBOLS:
        for tf in TIMEFRAMES:

            df = fetch_live_data(sym, tf)
            if df is None or len(df) < 200:
                print(f"⚠ Not enough data for {sym} {tf}")
                continue

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

            payload = {
                "symbol": sym,
                "side": side.upper(),
                "entry": round(entry, 6),
                "sl": round(sl, 6),
                "tp": round(tp, 6),
                "qty": None,
                "strategy_id": 2,
                "confidence": f"tf={tf}",
                "generated_at": now_utc.isoformat(),
            }

            all_signals.append(payload)

    print(f"✅ Generated {len(all_signals)} signals")
    return all_signals


# ================================
# UPLOAD SIGNÁLS
# ================================
def upload_to_backend(signals):
    if not BACKEND_URL:
        msg = "BACKEND_SIGNAL_UPDATE_URL not set in env!"
        print("❌", msg)
        return {"status": "error", "message": msg}

    if not signals:
        print("ℹ No signals to upload.")
        return {"status": "no_signals", "count": 0}

    try:
        print(f"📡 Uploading {len(signals)} signals → {BACKEND_URL}")
        resp = requests.post(BACKEND_URL, json=signals, timeout=30)

        print("🔁 Response:", resp.status_code, resp.text)

        resp.raise_for_status()
        return {
            "status": "uploaded",
            "count": len(signals),
            "backend_response": resp.json(),
        }

    except Exception as e:
        print("❌ Error uploading:", e)
        return {"status": "error", "message": str(e)}


# ================================
# MAIN ENTRYPOINT (API /run-strategy)
# ================================
def run_strategy_once():
    signals = generate_signals_once()
    result = upload_to_backend(signals)

    summary = {
        "generated_signals": len(signals),
        "upload_status": result,
        "signals": signals,
    }

    print("📊 Summary:", summary)
    return summary
if __name__ == "__main__":
    run_strategy_once()



