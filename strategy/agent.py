# agent.py

import os
import time
import pandas as pd
import ccxt
from datetime import datetime, timedelta

# ======================
# CONFIGURATION
# ======================
SYMBOLS = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
TIMEFRAMES = ["5m", "15m", "1h", "12h"]
DATA_DIR = "data"
LIMIT = 100000  # max candles per fetch

KEEP_DAYS_MAP = {
    "5m": 30,
    "15m": 60,
    "1h": 180,
    "12h": 365,
}

exchange = ccxt.binance({'enableRateLimit': True})

# ======================
# HELPERS
# ======================
def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def fetch_ohlcv(symbol: str, timeframe: str, since=None, limit=LIMIT):
    """Fetch OHLCV data from Binance with pagination"""
    all_data = []
    while True:
        candles = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
        if not candles:
            break
        all_data.extend(candles)
        since = candles[-1][0] + 1
        time.sleep(0.5)
        if len(candles) < limit:
            break
    return all_data


def load_existing_csv(symbol: str, timeframe: str):
    out_dir = os.path.join(DATA_DIR, symbol.replace("/", ""))
    out_path = os.path.join(out_dir, f"{timeframe}.csv")
    if os.path.exists(out_path):
        df = pd.read_csv(out_path, parse_dates=["ts"])
        return df, out_path
    return pd.DataFrame(), out_path


def update_csv(symbol: str, timeframe: str):
    """Update CSV with latest candles + auto-clean"""
    df_old, out_path = load_existing_csv(symbol, timeframe)

    if not df_old.empty:
        last_ts = int(df_old["ts"].iloc[-1].timestamp() * 1000)
    else:
        last_ts = None

    new_data = fetch_ohlcv(symbol, timeframe, since=last_ts)
    if not new_data and not df_old.empty:
        print(f"[SKIP] {symbol} {timeframe} already up-to-date.")
        return df_old, out_path

    df_new = pd.DataFrame(new_data, columns=["ts", "open", "high", "low", "close", "volume"])
    df_new["ts"] = pd.to_datetime(df_new["ts"], unit="ms")
    df_new[["open", "high", "low", "close", "volume"]] = df_new[
        ["open", "high", "low", "close", "volume"]
    ].astype(float)

    df_final = pd.concat([df_old, df_new]).drop_duplicates(subset="ts").reset_index(drop=True)

    # auto-clean
    keep_days = KEEP_DAYS_MAP.get(timeframe, 90)
    cutoff = datetime.now() - timedelta(days=keep_days)
    df_final = df_final[df_final["ts"] >= cutoff].reset_index(drop=True)

    ensure_dir(os.path.dirname(out_path))
    df_final.to_csv(out_path, index=False)
    print(f"[OK] {symbol} {timeframe} updated -> {len(df_final)} rows (kept {keep_days} days)")
    return df_final, out_path


def merge_timeframes(symbol: str, timeframes=TIMEFRAMES):
    """Merge multiple timeframe CSVs into one aligned dataset"""
    symbol_dir = os.path.join(DATA_DIR, symbol.replace("/", ""))
    merged = None

    for tf in timeframes:
        tf_path = os.path.join(symbol_dir, f"{tf}.csv")
        if not os.path.exists(tf_path):
            continue

        df = pd.read_csv(tf_path, parse_dates=["ts"])
        df = df[["ts", "open", "high", "low", "close", "volume"]]
        df = df.rename(columns={c: f"{c}_{tf}" for c in ["open","high","low","close","volume"]})

        if merged is None:
            merged = df
        else:
            merged = pd.merge_asof(
                merged.sort_values("ts"),
                df.sort_values("ts"),
                on="ts",
                direction="backward"
            )

    if merged is not None:
        out_path = os.path.join(symbol_dir, "merged_multi_tf.csv")
        merged.to_csv(out_path, index=False)
        print(f"[MERGED] {symbol} -> {out_path} ({len(merged)} rows)")
    else:
        print(f"[WARN] No data to merge for {symbol}")


# ======================
# MAIN
# ======================
if __name__ == "__main__":
    print(f"=== Daily Update Started @ {datetime.now()} ===")
    for sym in SYMBOLS:
        for tf in TIMEFRAMES:
            try:
                update_csv(sym, tf)
            except Exception as e:
                print(f"[ERR] {sym} {tf}: {e}")
        # After all timeframes updated → merge them
        merge_timeframes(sym)
    print(f"=== Update Finished @ {datetime.now()} ===")
