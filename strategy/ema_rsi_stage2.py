# ema_rsi_stage2.py
import ta
import numpy as np

def ensure_sl_tp_orientation(side: str, entry: float, sl: float, tp: float):
    """
    Ensure SL/TP follow convention:
      - LONG:  SL < entry < TP
      - SHORT: TP < entry < SL
    If not, fix automatically (swap or nudge slightly).
    """
    if side.lower() == "long":
        # if SL >= entry or TP <= entry, correct them
        if sl >= entry:
            sl = entry - abs(entry - sl) - 1e-6
        if tp <= entry:
            tp = entry + abs(tp - entry) + 1e-6
    else:  # short
        if sl <= entry:
            sl = entry + abs(entry - sl) + 1e-6
        if tp >= entry:
            tp = entry - abs(tp - entry) - 1e-6
    return sl, tp

def ema_rsi_strategy(df, i, adx_threshold=20):
    """
    Stage-2 EMA+RSI strategy with ADX filter and ATR-based dynamic SL/TP.
    returns (side, SL, TP) or None.
    """
    # compute indicators once
    if "EMA50" not in df:
        df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)
        df["EMA200"] = ta.trend.ema_indicator(df["close"], window=200)
        df["RSI"] = ta.momentum.rsi(df["close"], window=14)
        df["ATR"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=14)
        df["ADX"] = ta.trend.adx(df["high"], df["low"], df["close"], window=14).fillna(0)

    # protect against NaNs early in series
    if i < 200 or np.isnan(df["ATR"].iloc[i]) or np.isnan(df["EMA50"].iloc[i]) :
        return None

    price = float(df["close"].iloc[i])
    atr = float(df["ATR"].iloc[i])
    adx = float(df["ADX"].iloc[i])
    rsi = float(df["RSI"].iloc[i])
    ema50 = float(df["EMA50"].iloc[i])
    ema200 = float(df["EMA200"].iloc[i])

    # Trend strength filter
    if adx < adx_threshold:
        return None

    # LONG rules
    if ema50 > ema200 and rsi < 75:
        sl = price - 1.0 * atr      # tighter SL for stage-2
        tp = price + 1.8 * atr
        sl, tp = ensure_sl_tp_orientation("long", price, sl, tp)
        return ("long", sl, tp)

    # SHORT rules
    if ema50 < ema200 and rsi > 25:
        sl = price + 1.0 * atr
        tp = price - 1.8 * atr
        sl, tp = ensure_sl_tp_orientation("short", price, sl, tp)
        return ("short", sl, tp)

    return None
