 

# 💹 Semi automated trading Framework

### *“Quant-Level Strategy Power. Human-Level Control ”*

An **end-to-end semi-automated trading ecosystem** combining multi-stage signal generation (EMA-RSI strategy), backtesting, live-signal monitoring, and an interactive dashboard for performance control and visualization.

---

## 🧭 Overview

**Semi-automated trading framework** unifies algorithmic strategy design and dashboard-based monitoring:

* ⚙️ **Backend (Python)** — Multi-stage EMA-RSI trading pipeline with adaptive filtering and backtesting.
* 🖥 **Frontend (React.js)** — Interactive trading dashboard for risk control, visualization, and signal management.
* 🔗 **FastAPI Layer** — Bridges strategy output and live dashboards.

---

## 🧠 Core Components

| Module                    | Description                                                                   |
| ------------------------- | ----------------------------------------------------------------------------- |
| **Trading Bot**           | Multi-stage EMA-RSI strategy with live signal tracking and CSV-based outputs. |
| **Backtester**            | Evaluates strategy performance metrics (win rate, drawdown, PnL).             |
| **Dashboard (Frontend)**  | React-based interface for viewing and managing signals, orders, and PnL.      |
| **Backend API (FastAPI)** | Provides REST endpoints for user auth, risk settings, and data sync.          |

---

## 📦 Project Structure

```
📁 binance-abcd/
│
├── frontend/                 # React.js dashboard
│   └── README.md             # Frontend documentation
│
├── backend/                  # FastAPI backend (optional)
│   └── README.md             # Backend setup guide
│
├── strategy/                 # Core EMA-RSI and backtesting modules
│
├── requirements.txt
├── structure.txt
└── README.md                 # (You’re here)
```

---

## 🚀 Features

| Category                | Highlights                                              |
| ----------------------- | ------------------------------------------------------- |
| **Signal Engine**       | Multi-stage EMA-RSI refinement pipeline (no ML).        |
| **Backtesting**         | Statistical evaluation and summary export.              |
| **Live Signal Logging** | Timestamped real-time suggestions.                      |
| **Dashboard**           | Intuitive frontend to visualize trades and performance. |
| **Risk Control**        | Adjustable risk %, capital, and max loss.               |
| **Auth & Security**     | JWT-based secure user authentication.                   |
| **Modularity**          | Each module can run independently or in sync.           |

---

## 🧩 Workflow

1. **Generate Signals** → `ema_rsi.py`
2. **Filter & Refine** → `run_stage2.py`
3. **Backtest** → `run_stage3.py`
4. **Live Log** → `run_stage4.py`
5. **Monitor via Dashboard** → React UI connects through FastAPI

---

## ⚙️ Setup

### 1️⃣ Clone the Repository

```bash
git clone https://...........
cd ...
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run Frontend Dashboard

```bash
cd frontend
npm install
npm start
```

### 4️⃣ Execute Strategy

```bash
cd strategy
python run_stage2.py
```

---

## 📈 Example Use Case

* Generate and analyze buy/sell signals on equities or crypto pairs
* Run performance simulations using historical data
* Log live signal flow and monitor PnL through the dashboard

---

## 🧩 Folder Documentation

* [📘 Frontend Docs](frontend/README.md)
* [⚙️ Backend Setup](backend/README.md)
* [📊 Strategy & Bot Guide](strategy/README.md) 
---

## 🧠 Tech Stack

| Layer            | Technology                  |
| ---------------- | --------------------------- |
| **Frontend**     | React.js, Axios, Recharts   |
| **Backend**      | FastAPI, Python, SQLAlchemy |
| **Trading Core** | Pandas, NumPy, Matplotlib   |
| **Database**     | PostgreSQL                  |
| **Auth**         | JWT Tokens                  |

---

## 🧪 Future Enhancements

* WebSocket-based live data streaming
* Reinforcement-learning strategy optimizer
* Integrated deployment pipeline (Docker + CI/CD)
* Streamlit analytics dashboard

---

## 🏁 Authors

* Sri Karthik Reddy
* Adhwika
* Shivani
  

---

## ⭐ Support

If this project inspires you or helps your workflow —
please **⭐ star** the repository on GitHub.
Your support fuels future improvements!

---
