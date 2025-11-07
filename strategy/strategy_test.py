# strategy_test.py

import pandas as pd
import ta
import matplotlib.pyplot as plt

# -------------------------
# Step 1: Load & Clean Data
# -------------------------
import glob

# Merge multiple CSVs in the folder
files = glob.glob("BTCUSDT-5m-2025-09/*.csv")
df_list = []
for file in files:
    temp = pd.read_csv(file, header=None)
    temp.columns = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ]
    temp = temp[["open_time","open","high","low","close","volume"]]
    temp["open_time"] = pd.to_datetime(temp["open_time"].round(0).astype("int64"), unit="ms", errors="coerce")
    temp[["open","high","low","close","volume"]] = temp[["open","high","low","close","volume"]].astype(float)
    df_list.append(temp)

df = pd.concat(df_list, ignore_index=True)

# -------------------------
# Step 2: Indicators
# -------------------------
df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)
df["EMA200"] = ta.trend.ema_indicator(df["close"], window=200)
df["RSI"] = ta.momentum.rsi(df["close"], window=14)
df["ATR"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=14)

# -------------------------
# Step 3: Strategy Logic & Backtest
# -------------------------
balance = 10000
risk = 0.02
equity_curve = []

position = None
trade_history = []

for i in range(200, len(df)):
    price = df["close"].iloc[i]
    time = df["open_time"].iloc[i]

    # Close position if TP or SL is hit
    if position:
        if price <= position["SL"]:   # stop-loss
            balance -= position["risk_amt"]
            position["result"] = "SL"
            position["exit_price"] = price
            position["exit_time"] = time
            trade_history.append(position)
            position = None
        elif price >= position["TP"]: # take-profit
            balance += position["reward_amt"]
            position["result"] = "TP"
            position["exit_price"] = price
            position["exit_time"] = time
            trade_history.append(position)
            position = None

    # Open new position
    if not position:
        if df["EMA50"].iloc[i] > df["EMA200"].iloc[i] and df["RSI"].iloc[i] < 70:
            atr = df["ATR"].iloc[i]
            entry = price
            sl = entry - 1.5 * atr
            tp = entry + 2 * atr

            risk_amt = balance * risk
            reward_amt = risk_amt * (2/1.5)
            position = {
                "entry_time": time,
                "entry": entry,
                "SL": sl,
                "TP": tp,
                "risk_amt": risk_amt,
                "reward_amt": reward_amt,
                "result": None
            }

    equity_curve.append(balance)

# -------------------------
# Step 4: Results
# -------------------------
print("Final Balance:", round(balance,2))
print("Net Profit:", round(balance-10000,2))
print("Total Trades Closed:", len(trade_history))

# Print first 5 trade details
for t in trade_history[:5]:
    print(t)

# -------------------------
# Step 5: Plot Equity Curve
# -------------------------
plt.figure(figsize=(12,6))
plt.plot(equity_curve, label="Equity Curve")
plt.title("Strategy Equity Curve")
plt.xlabel("Time Steps (5-min bars)")
plt.ylabel("Balance")
plt.legend()
plt.show()
