# 🧠 Automated Trading Bot – Multi-Stage EMA-RSI Strategy

This repository contains a **semi-automated trading framework** that integrates multi-stage EMA-RSI strategies with adaptive filtering, backtesting, and live signal generation.
It enables an **end-to-end workflow** from signal creation to real-time trade suggestion — built for performance analysis, experimentation, and live deployment.

---

## 🚀 Key Features

### ⚙️ EMA-RSI Core Strategy

Generates raw buy/sell signals using exponential moving averages and RSI thresholds for dynamic entry–exit detection.

### 🧩 Multi-Stage Architecture

* **Stage 1:** Base signal generation using EMA-RSI rules
* **Stage 2:** Signal refinement through advanced filtering and noise reduction
* **Stage 3:** Backtesting and result validation with historical data
* **Stage 4:** Aggregation, enhancement, and live signal monitoring — *no machine learning used*

### 📈 Custom Backtesting Engine

`backtester.py` computes win rates, drawdowns, and profit metrics, saving results to `backtest_summary.csv`.

### 🕒 Live Signal Logging

Continuous generation of timestamped trade suggestions via `live_signals_log.csv`.

### 🧩 Modular & Lightweight

Each stage runs independently, allowing flexible experimentation and easy integration into custom data pipelines.

---

## 📂 Project Structure

```
📁 project/
│
├── agent.py                   # Handles live trade signal logic
├── autoload.py                # Loads and preprocesses market data
├── backtester.py              # Backtesting and performance metrics
├── ema_rsi.py                 # Core EMA-RSI signal generator (Stage 1)
├── ema_rsi_stage2.py          # Stage 2 – refined signal filtering
├── run_stage2.py              # Executes Stage 2 process
├── run_stage3.py              # Executes Stage 3 – backtesting
├── run_stage4.py              # Executes Stage 4 – live signal updates
├── merge.py                   # Combines output logs from multiple stages
├── trade_suggestions.csv      # Stage 1 trade calls
├── trade_suggestions_stage2.csv / .json  # Stage 2 refined signals
├── live_signals_log.csv       # Live trade updates
├── backtest_summary.csv       # Performance summaries
├── structure.txt              # File hierarchy reference
├── download_log.txt           # Data fetch logs
└── readme.txt                 # Local project summary
```

---

## 🧩 Workflow Overview

1. **Signal Generation** → `ema_rsi.py`
2. **Refinement & Filtering** → `run_stage2.py`
3. **Backtesting & Validation** → `run_stage3.py`
4. **Aggregation & Live Logging** → `run_stage4.py`

---

## 📊 Outputs

| File                                 | Description                  |
| ------------------------------------ | ---------------------------- |
| `trade_suggestions.csv / stage2.csv` | Generated trading signals    |
| `backtest_summary.csv`               | Strategy performance results |
| `live_signals_log.csv`               | Real-time signal updates     |

---

## 🧠 Tech Stack

| Category       | Tools                        |
| -------------- | ---------------------------- |
| **Language**   | Python                       |
| **Libraries**  | Pandas, NumPy, Matplotlib    |
| **Data Input** | Historical OHLCV market data |
| **Execution**  | CLI-based modular scripts    |

---

## ⚙️ Setup

```bash
git clone https://github.com/yourusername/trade-bot.git
cd trade-bot
pip install -r requirements.txt
```

Run any stage:

```bash
python run_stage2.py
```

---

## 📈 Use Cases

* Evaluate EMA-RSI performance across multiple timeframes
* Refine and backtest strategies using real historical data
* Monitor live market signals and analyze their evolution

---

## 🧩 Future Enhancements

* Dashboard visualization using Streamlit
* Integration with API-based real-time data feeds
* Reinforcement-learning-based strategy optimization

---

