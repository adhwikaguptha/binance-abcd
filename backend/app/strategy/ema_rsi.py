# ema_rsi.py

import ta

def ema_rsi_strategy(df, i):
    """
    Returns (side, SL, TP) or None
    Dynamic ATR-based SL/TP + trend confirmation
    """
    # Compute indicators only once
    if "EMA50" not in df:
        df["EMA50"] = ta.trend.ema_indicator(df["close"], 50)
        df["EMA200"] = ta.trend.ema_indicator(df["close"], 200)
        df["RSI"] = ta.momentum.rsi(df["close"], 14)
        df["ATR"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"], 14)
        df["ADX"] = ta.trend.adx(df["high"], df["low"], df["close"], 14)

    price = df["close"].iloc[i]
    atr = df["ATR"].iloc[i]
    adx = df["ADX"].iloc[i]

    # Only trade strong trends (ADX > 20)
    if adx < 20:
        return None

    # Dynamic SL/TP
    if df["EMA50"].iloc[i] > df["EMA200"].iloc[i] and df["RSI"].iloc[i] < 70:
        sl = price - 1.0 * atr      # tighter SL
        tp = price + 2.0 * atr      # wider TP
        return ("long", sl, tp)

    if df["EMA50"].iloc[i] < df["EMA200"].iloc[i] and df["RSI"].iloc[i] > 30:
        sl = price + 1.0 * atr
        tp = price - 2.0 * atr
        return ("short", sl, tp)

    return None
