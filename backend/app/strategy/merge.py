# merge.py

import os
import pandas as pd

DATA_DIR = "data"   # where your CSVs are stored
TIMEFRAMES = ["5m", "15m", "1h", "12h"]


def load_timeframe(symbol: str, timeframe: str) -> pd.DataFrame:
    """Load one timeframe CSV for given symbol"""
    path = os.path.join(DATA_DIR, symbol, f"{timeframe}.csv")
    if not os.path.exists(path):
        print(f"[WARN] Missing file: {path}")
        return pd.DataFrame()
    
    df = pd.read_csv(path, parse_dates=["ts"])
    df = df[["ts", "open", "high", "low", "close", "volume"]]
    
    # Add suffix for columns to avoid clashes
    suffix = f"_{timeframe}"
    df = df.rename(columns={c: c + suffix for c in ["open","high","low","close","volume"]})
    return df


def merge_timeframes(symbol: str, timeframes=TIMEFRAMES) -> pd.DataFrame:
    """Merge multiple timeframe CSVs into one aligned dataset"""
    merged = None
    for tf in timeframes:
        df = load_timeframe(symbol, tf)
        if df.empty:
            continue
        if merged is None:
            merged = df
        else:
            merged = pd.merge_asof(
                merged.sort_values("ts"),
                df.sort_values("ts"),
                on="ts",
                direction="backward"  # align smaller candles to latest higher timeframe
            )
    return merged


def merge_all_symbols():
    """Loop over all symbol folders and create merged dataset"""
    for symbol_folder in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, symbol_folder)
        if not os.path.isdir(folder_path):
            continue

        print(f"\n[INFO] Processing {symbol_folder}...")
        merged_df = merge_timeframes(symbol_folder)

        if merged_df is None or merged_df.empty:
            print(f"[SKIP] No data for {symbol_folder}")
            continue

        out_path = os.path.join(folder_path, "merged_multi_tf.csv")
        merged_df.to_csv(out_path, index=False)
        print(f"[OK] Saved {out_path} ({len(merged_df)} rows)")


if __name__ == "__main__":
    merge_all_symbols()
