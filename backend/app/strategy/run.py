# run.py
import os
import pandas as pd
from backtester import Backtester
from ema_rsi import ema_rsi_strategy  # your strategy
from datetime import timedelta

DATA_DIR = "data"
TIMEFRAMES = ["5m", "15m", "1h", "12h"]
SUGGESTIONS_CSV = "trade_suggestions.csv"

def load_data(symbol: str, timeframe: str):
    path = os.path.join(DATA_DIR, symbol.replace("/", ""), f"{timeframe}.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df["ts"] = pd.to_datetime(df["ts"])
    df[["open","high","low","close","volume"]] = df[["open","high","low","close","volume"]].astype(float)
    return df

def compute_signal_stats(trade_history, side):
    """Compute win probability, avg duration, RR ratio"""
    if not trade_history:
        return 0, 0, 0
    # Filter trades by side
    trades = [t for t in trade_history if t["side"] == side]
    if not trades:
        return 0, 0, 0
    wins = [t for t in trades if t["result"]=="TP"]
    win_prob = len(wins)/len(trades)*100

    durations = [(t["exit_time"] - t["entry_time"]).total_seconds()/60 for t in trades]
    avg_duration = round(sum(durations)/len(durations)) if durations else 0

    rr_ratios = [abs(t["TP"] - t["entry"])/abs(t["entry"] - t["SL"]) for t in trades]
    avg_rr = round(sum(rr_ratios)/len(rr_ratios),2) if rr_ratios else 0

    return win_prob, avg_duration, avg_rr

def generate_trade_suggestions(symbols):
    suggestions = []

    for sym in symbols:
        for tf in TIMEFRAMES:
            df = load_data(sym, tf)
            if df is None or len(df)<200:
                continue

            bt = Backtester(df, ema_rsi_strategy)
            results = bt.run()

            # Take last candle signal
            signal = ema_rsi_strategy(df, len(df)-1)
            if signal is None:
                continue

            side, sl, tp = signal
            last_price = df["close"].iloc[-1]

            # Compute historical stats
            win_prob, avg_duration, avg_rr = compute_signal_stats(results["trades"], side)

            suggestions.append({
                "symbol": sym,
                "timeframe": tf,
                "side": side.upper(),
                "entry": round(last_price,2),
                "SL": round(sl,2),
                "TP": round(tp,2),
                "expected_duration_min": avg_duration,
                "win_probability": round(win_prob,2),
                "avg_rr": avg_rr
            })

    return pd.DataFrame(suggestions)

if __name__ == "__main__":
    # detect symbols from folders
    symbols = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    symbols = [s.replace("USDT","/USDT") for s in symbols]

    df_suggestions = generate_trade_suggestions(symbols)
    print("\n=== TRADE SUGGESTIONS ===")
    print(df_suggestions)

    df_suggestions.to_csv(SUGGESTIONS_CSV, index=False)
    print(f"\nSaved trade suggestions -> {SUGGESTIONS_CSV}")
