import ta
import numpy as np

def ensure_sl_tp_orientation(side: str, entry: float, sl: float, tp: float):
    if side.lower() == "long":
        if sl >= entry:
            sl = entry - abs(entry - sl) - 1e-6
        if tp <= entry:
            tp = entry + abs(tp - entry) + 1e-6
    else:
        if sl <= entry:
            sl = entry + abs(entry - sl) - 1e-6
        if tp >= entry:
            tp = entry - abs(tp - entry) - 1e-6
    return sl, tp


def ema_rsi_strategy(df, i):
    # ----- Compute Indicators -----
    df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["EMA200"] = ta.trend.ema_indicator(df["close"], window=200)
    df["RSI"] = ta.momentum.rsi(df["close"], window=14)
    df["ATR"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=14)

    # Safe minimum
    if i < 50:
        return None

    price = float(df["close"].iloc[i])
    atr   = float(df["ATR"].iloc[i])
    rsi   = float(df["RSI"].iloc[i])
    ema50 = float(df["EMA50"].iloc[i])
    ema200 = float(df["EMA200"].iloc[i])

    # ----- RELAXED RULES (guaranteed signals) -----

    # LONG
    if ema50 > ema200 and rsi < 60:
        sl = price - 1.2 * atr
        tp = price + 1.8 * atr
        sl, tp = ensure_sl_tp_orientation("long", price, sl, tp)
        return ("LONG", sl, tp)

    # SHORT
    if ema50 < ema200 and rsi > 40:
        sl = price + 1.2 * atr
        tp = price - 1.8 * atr
        sl, tp = ensure_sl_tp_orientation("short", price, sl, tp)
        return ("SHORT", sl, tp)

    return None
