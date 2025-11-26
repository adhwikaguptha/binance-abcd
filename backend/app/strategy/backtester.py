import pandas as pd
import numpy as np

class Backtester:
    def __init__(self, df, strategy, initial_balance=10000, risk=0.02):
        self.df = df.copy()
        self.strategy = strategy
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.risk = risk
        self.equity_curve = []
        self.trade_history = []
        self.position = None

    def run(self):
        self.tp_hits = 0
        self.sl_hits = 0
        self.max_drawdown = 0
        peak = self.balance

        for i in range(200, len(self.df)):
            price = self.df["close"].iloc[i]
            time = self.df["ts"].iloc[i]

            # --- Manage Open Trade ---
            if self.position:
                side = self.position["side"]
                if side == "long":
                    if price <= self.position["SL"]:
                        self._close_trade("SL", price, time)
                        self.sl_hits += 1
                    elif price >= self.position["TP"]:
                        self._close_trade("TP", price, time)
                        self.tp_hits += 1
                elif side == "short":
                    if price >= self.position["SL"]:
                        self._close_trade("SL", price, time)
                        self.sl_hits += 1
                    elif price <= self.position["TP"]:
                        self._close_trade("TP", price, time)
                        self.tp_hits += 1

            # --- Entry Logic ---
            if not self.position:
                signal = self.strategy(self.df, i)
                if signal:
                    self._open_trade(signal, price, time)

            # Update equity
            self.equity_curve.append(self.balance)
            peak = max(peak, self.balance)
            drawdown = peak - self.balance
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown

        # Compute win rate
        win_rate = (self.tp_hits / len(self.trade_history) * 100) if self.trade_history else 0

        return {
            "final_balance": self.balance,
            "net_profit": self.balance - self.initial_balance,
            "trades": self.trade_history,
            "equity_curve": self.equity_curve,
            "tp_hits": self.tp_hits,
            "sl_hits": self.sl_hits,
            "win_rate": round(win_rate, 2),
            "max_drawdown": round(self.max_drawdown, 2)
        }

    def _open_trade(self, signal, price, time):
        side, sl, tp = signal
        risk_amt = self.balance * self.risk

        self.position = {
            "side": side,
            "entry_time": time,
            "entry": price,
            "SL": sl,
            "TP": tp,
            "risk_amt": risk_amt,
            "reward_amt": risk_amt * (abs(tp - price) / abs(price - sl)),
        }

    def _close_trade(self, result, exit_price, exit_time):
        if result == "SL":
            self.balance -= self.position["risk_amt"]
        else:
            self.balance += self.position["reward_amt"]

        self.position["result"] = result
        self.position["exit_price"] = exit_price
        self.position["exit_time"] = exit_time
        self.trade_history.append(self.position)
        self.position = None
