import os
from datetime import datetime, timezone
import pandas as pd
import ccxt
import requests

# Try absolute import (backend)
try:
    from app.strategy.ema_rsi_stage2 import ema_rsi_strategy
except ImportError:
    # Local fallback
    from ema_rsi_stage2 import ema_rsi_strategy


# -----------------------------------------
# CONFIG
# -----------------------------------------
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

BACKEND_URL = os.getenv("BACKEND_SIGNAL_UPDATE_URL")
# Example:
# https://binance-abcd-production.up.railway.app/signals/update_active


# -----------------------------------------
# FETCH LIVE DATA
# -----------------------------------------
def fetch_live_data(symbol: str, timeframe: str) -> pd.DataFrame:
    ex = ccxt.binance()

    ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=LIMIT_CANDLES)

    df = pd.DataFrame(
        ohlcv,
        columns=["ts", "open", "high", "low", "close", "volume"],
    )
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    df[["open", "high", "low", "close", "volume"]] = \
        df[["open", "high", "low", "close", "volume"]].astype(float)

    return df


# -----------------------------------------
# GENERATE SIGNALS
# -----------------------------------------
def generate_signals_once():
    all_signals = []
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    for sym in SYMBOLS:
        for tf in TIMEFRAMES:

            # Fetch OHLCV
            try:
                df = fetch_live_data(sym, tf)
            except Exception as e:
                print(f"⚠ Failed to fetch {sym} ({tf}): {e}")
                continue

            idx = len(df) - 1

            # Apply strategy
            try:
                strat = ema_rsi_strategy(df, idx)
            except Exception as e:
                print(f"⚠ Strategy error for {sym} {tf}: {e}")
                continue

            if strat is None:
                continue

            side, sl, tp = strat
            entry = float(df["close"].iloc[-1])

            # Build payload matching SignalCreate
            signal = {
                "symbol": sym,
                "side": side.upper(),
                "entry": round(entry, 6),
                "sl": round(sl, 6),
                "tp": round(tp, 6),
                "qty": None,                # let backend decide
                "strategy_id": 2,
                "confidence": f"timeframe={tf}",
                "generated_at": now.isoformat(),
            }

            all_signals.append(signal)

    print(f"✅ Generated {len(all_signals)} signals")
    return all_signals


# -----------------------------------------
# UPLOAD SIGNALS TO BACKEND
# -----------------------------------------
def upload_to_backend(signals):
    if not BACKEND_URL:
        msg = "❌ BACKEND_SIGNAL_UPDATE_URL not set"
        print(msg)
        return {"status": "error", "message": msg}

    if not signals:
        print("ℹ No signals to upload")
        return {"status": "no_signals", "count": 0}

    try:
        print(f"📡 Uploading {len(signals)} signals → {BACKEND_URL}")
        resp = requests.post(BACKEND_URL, json=signals, timeout=20)

        print("🔁 Response code:", resp.status_code)
        print("🔁 Body:", resp.text)

        resp.raise_for_status()

        return {
            "status": "uploaded",
            "count": len(signals),
            "backend_response": resp.json(),
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# -----------------------------------------
# MAIN ENTRY
# -----------------------------------------
def run_strategy_once():
    print("\n🚀 Running EMA+RSI strategy once...")

    sigs = generate_signals_once()
    upload = upload_to_backend(sigs)

    out = {
        "generated_signals": len(sigs),
        "upload_status": upload,
        "signals": sigs,
    }

    print("📊 Summary:", out)
    return out



