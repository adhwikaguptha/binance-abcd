import numpy as np
import ta


# ============================
# Ensure SL/TP are on correct side
# ============================
def ensure_sl_tp_orientation(side: str, entry: float, sl: float, tp: float):
    """
    Guarantee correct SL/TP orientation:
      - LONG:  SL < entry < TP
      - SHORT: TP < entry < SL
    Auto-fixes any mistakes.
    """
    if side.lower() == "long":
        if sl >= entry:
            sl = entry - abs(sl - entry) - 1e-6
        if tp <= entry:
            tp = entry + abs(entry - tp) + 1e-6
    else:
        if sl <= entry:
            sl = entry + abs(entry - sl) + 1e-6
        if tp >= entry:
            tp = entry - abs(tp - entry) - 1e-6

    return sl, tp


# ============================
# EMA + RSI + ADX Strategy
# ============================
def ema_rsi_strategy(df, i, adx_threshold=18):
    """
    Stage-2 EMA+RSI strategy with:
      ✓ EMA50 vs EMA200 trend
      ✓ RSI overbought/oversold
      ✓ ADX trend-strength filter
      ✓ ATR-based volatility SL/TP
    Returns:
      ("long" | "short", SL, TP)
      OR None (no signal)
    """

    # --- Compute indicators (only once) ---
    if "EMA50" not in df:
        df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)
        df["EMA200"] = ta.trend.ema_indicator(df["close"], window=200)
        df["RSI"] = ta.momentum.rsi(df["close"], window=14)
        df["ATR"] = ta.volatility.average_true_range(
            df["high"], df["low"], df["close"], window=14
        )
        df["ADX"] = ta.trend.adx(
            df["high"], df["low"], df["close"], window=14
        )

        # Replace NaN values with safe defaults
        df.fillna(method="bfill", inplace=True)
        df.fillna(method="ffill", inplace=True)

    # --- Reject early candles (insufficient data) ---
    if i < 200:
        return None

    price = float(df["close"].iloc[i])
    ema50 = float(df["EMA50"].iloc[i])
    ema200 = float(df["EMA200"].iloc[i])
    rsi = float(df["RSI"].iloc[i])
    atr = float(df["ATR"].iloc[i])
    adx = float(df["ADX"].iloc[i])

    # --- ADX filter ---
    if adx < adx_threshold:
        return None

    # ============================
    # LONG SETUP
    # ============================
    if ema50 > ema200 and rsi < 70:
        sl = price - 1.2 * atr
        tp = price + 2.0 * atr
        sl, tp = ensure_sl_tp_orientation("long", price, sl, tp)
        return ("long", sl, tp)

    # ============================
    # SHORT SETUP
    # ============================
    if ema50 < ema200 and rsi > 30:
        sl = price + 1.2 * atr
        tp = price - 2.0 * atr
        sl, tp = ensure_sl_tp_orientation("short", price, sl, tp)
        return ("short", sl, tp)

    return None
