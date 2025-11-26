# run_stage2.py
import os
import math
import pandas as pd
from datetime import datetime
from backtester import Backtester
from ema_rsi_stage2 import ema_rsi_strategy

DATA_DIR = "data"
TIMEFRAMES = ["5m", "15m", "1h", "12h"]
SUGGESTIONS_CSV = "trade_suggestions_stage2.csv"
SUGGESTIONS_JSON = "trade_suggestions_stage2.json"

# Register strategies here (name -> function)
STRATEGIES = {
    "ema_rsi": ema_rsi_strategy,
    # add more strategies here in future
}

RECENT_TRADE_WINDOW = 50   # use last N trades for statistics (Stage-2 uses recent history)

def load_df(symbol: str, timeframe: str):
    """Load CSV or ZIP file for given symbol/timeframe"""
    base_path = os.path.join(DATA_DIR, symbol.replace("/", ""))
    csv_path = os.path.join(base_path, f"{timeframe}.csv")
    zip_path = os.path.join(base_path, f"{timeframe}.zip")

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    elif os.path.exists(zip_path):
        df = pd.read_csv(zip_path, compression='zip')
    else:
        print(f"[WARN] No data found for {symbol} {timeframe} in {base_path}")
        return None

    # Clean + format
    df["ts"] = pd.to_datetime(df["ts"])
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df


def sample_recent_trades(trades, side, n=RECENT_TRADE_WINDOW):
    # filter by side and take last n trades by entry_time
    trades_side = [t for t in trades if t.get("side","").lower() == side.lower()]
    trades_side_sorted = sorted(trades_side, key=lambda x: x["entry_time"])  # oldest->newest
    return trades_side_sorted[-n:]

def compute_side_stats(trades, side):
    """Compute win_prob (%), avg_duration (minutes), avg_rr from recent trades of same side"""
    recent = sample_recent_trades(trades, side, RECENT_TRADE_WINDOW)
    if not recent:
        return 0.0, 0.0, 0.0, 0  # win_prob, avg_dur_min, avg_rr, sample_size

    sample_size = len(recent)
    wins = sum(1 for t in recent if t.get("result") == "TP")
    win_prob = wins / sample_size * 100.0

    # durations and rr
    durations = []
    rrs = []
    for t in recent:
        # ensure exit_time/entry_time are datetimes
        et = t.get("exit_time")
        st = t.get("entry_time")
        if isinstance(et, str):
            et = pd.to_datetime(et)
        if isinstance(st, str):
            st = pd.to_datetime(st)
        if et is not None and st is not None:
            dur_min = (et - st).total_seconds() / 60.0
            durations.append(dur_min)
        # rr: (TP-entry)/(entry-SL) absolute
        try:
            rr = abs(t.get("TP",0) - t.get("entry",0)) / max(1e-9, abs(t.get("entry",0) - t.get("SL",0)))
            rrs.append(rr)
        except Exception:
            pass

    avg_dur = round(sum(durations)/len(durations)) if durations else 0
    avg_rr = round(sum(rrs)/len(rrs), 2) if rrs else 0.0

    return round(win_prob,2), int(avg_dur), avg_rr, sample_size

def confidence_label(win_prob, avg_rr, sample_size):
    """Simple label rules for Stage-2"""
    if sample_size >= 20 and win_prob >= 60 and avg_rr >= 1.5:
        return "HIGH"
    if sample_size >= 10 and (win_prob >= 55 and avg_rr >= 1.2):
        return "MEDIUM"
    return "LOW"

def build_suggestions(symbols):
    suggestions = []
    now = datetime.utcnow().isoformat()

    for sym in symbols:
        for tf in TIMEFRAMES:
            df = load_df(sym, tf)
            if df is None or len(df) < 300:
                # skip insufficient data
                continue

            for sname, sfunc in STRATEGIES.items():
                # run backtest to get historical trades (you may cache this in prod)
                bt = Backtester(df, sfunc)
                results = bt.run()
                trades = results.get("trades", [])

                # compute latest signal on last candle
                sig = sfunc(df, len(df)-1)
                if sig is None:
                    continue
                side, sl, tp = sig
                entry = float(df["close"].iloc[-1])

                # safety: ensure SL/TP orientation using simple checks (extra guard)
                if side.lower() == "long":
                    if not (sl < entry < tp):
                        # recompute/correct
                        if sl >= entry:
                            sl = entry - abs(sl-entry) - 1e-6
                        if tp <= entry:
                            tp = entry + abs(tp-entry) + 1e-6
                else:
                    if not (tp < entry < sl):
                        if sl <= entry:
                            sl = entry + abs(sl-entry) + 1e-6
                        if tp >= entry:
                            tp = entry - abs(tp-entry) - 1e-6

                # compute stats for side
                win_prob, avg_dur, avg_rr, sample_size = compute_side_stats(trades, side)
                conf = confidence_label(win_prob, avg_rr, sample_size)

                rr_ratio_live = round(abs(tp - entry) / max(1e-9, abs(entry - sl)), 2)

                suggestion = {
                    "generated_at": now,
                    "symbol": sym,
                    "timeframe": tf,
                    "strategy": sname,
                    "side": side.upper(),
                    "entry": round(entry, 6),
                    "SL": round(sl, 6),
                    "TP": round(tp, 6),
                    "expected_duration_min": avg_dur,
                    "win_probability": win_prob,
                    "avg_rr": avg_rr,
                    "rr_ratio_live": rr_ratio_live,
                    "confidence": conf,
                    "sample_size": sample_size
                }
                suggestions.append(suggestion)

    return suggestions

if __name__ == "__main__":
    # detect symbols (folders in data/)
    symbols = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    # symbols folder names might be like 'BTCUSDT' so convert to 'BTC/USDT'
    symbols = [s.replace("USDT","/USDT") for s in symbols]

    suggestions = build_suggestions(symbols)
    if not suggestions:
        print("No suggestions generated.")
    else:
        df = pd.DataFrame(suggestions)
        print(df)
        df.to_csv(SUGGESTIONS_CSV, index=False)
        # json for API/frontend
        with open(SUGGESTIONS_JSON, "w") as f:
            f.write(pd.DataFrame(suggestions).to_json(orient="records", date_format="iso"))
        print(f"\nSaved -> {SUGGESTIONS_CSV}, {SUGGESTIONS_JSON}")
