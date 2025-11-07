# run_stage4.py
import os
import pandas as pd
from datetime import datetime, timezone
import json
import ccxt
import requests
import time
from ema_rsi_stage2 import ema_rsi_strategy

# -----------------------------
# CONFIGURATION
# -----------------------------
SYMBOLS = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "XRP/USDT", "SOL/USDT"]
TIMEFRAMES = ["5m", "15m", "1h", "12h"]
TRADE_LOG = "live_signals_log.csv"
BACKEND_URL = "http://127.0.0.1:8000/signals/update_active"
LIMIT_CANDLES = 300
FETCH_INTERVAL = 3600  # 1 hour in seconds

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
# GENERATE SIGNALS
# -----------------------------
def generate_signals(symbols, timeframes):
    live_signals = []

    for sym in symbols:
        for tf in timeframes:
            try:
                df = fetch_live_data(sym, tf)
            except Exception as e:
                print(f"⚠️ Error fetching {sym} {tf}: {e}")
                continue

            sig = ema_rsi_strategy(df, len(df) - 1)
            if sig is None:
                continue

            side, sl, tp = sig
            entry = float(df["close"].iloc[-1])
            rr_ratio = round(abs(tp - entry) / max(1e-9, abs(entry - sl)), 2)

            signal = {
                "symbol": sym,
                "side": side.upper(),
                "entry": round(entry, 6),
                "sl": round(sl, 6),
                "tp": round(tp, 6),
            }
            live_signals.append(signal)
            print(f"[{sym} | {tf}] {side.upper()} → Entry={entry}, SL={sl}, TP={tp}, RR={rr_ratio}")

    return live_signals

# -----------------------------
# LOG & UPLOAD SIGNALS
# -----------------------------
def log_and_upload(signals):
    if not signals:
        print("⚠️ No signals generated this cycle.")
        return

    # Save locally
    df = pd.DataFrame(signals)
    if os.path.exists(TRADE_LOG):
        df_existing = pd.read_csv(TRADE_LOG)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(TRADE_LOG, index=False)
    print(f"💾 Saved {len(signals)} signals to {TRADE_LOG}")

    # Upload to backend
    try:
        resp = requests.post(BACKEND_URL, json=signals, timeout=10)
        resp.raise_for_status()
        print(f"✅ Uploaded {len(signals)} signals to backend (HTTP {resp.status_code})")
    except Exception as e:
        print(f"⚠️ Error sending signals: {e}")

# -----------------------------
# MAIN LOOP
# -----------------------------
def main():
    print("🚀 Starting Stage 4 Signal Engine (runs every 1 hour)")
    while True:
        print("\n⏰ Running new signal generation cycle:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        signals = generate_signals(SYMBOLS, TIMEFRAMES)
        log_and_upload(signals)
        print("✅ Cycle complete. Sleeping for 1 hour...\n")
        time.sleep(FETCH_INTERVAL)

# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    main()
