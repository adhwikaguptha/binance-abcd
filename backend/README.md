Perfect — here’s a complete professional `README.md` for your FastAPI + Binance + PostgreSQL Trading Bot Backend project.

It’s designed exactly like a developer GitHub README — clean, structured, and detailed enough for both contributors and devs setting it up for the first time.

---

```markdown
Trading Bot Backend (FastAPI + Binance + PostgreSQL)

Overview
This repository contains the backend of a **semi-automated trading platform** powered by **FastAPI**, **PostgreSQL**, and **Binance Testnet** integration.  
It manages signals, executes trades, tracks open positions, monitors stop-loss/take-profit triggers, and calculates daily PnL (Profit & Loss).  

The system is fully modular, asynchronous, and production-ready — built for both **live deployment** and **paper trading**.

---
Tech Stack

| Component | Purpose |
|------------|----------|
| FastAPI | Core backend framework for asynchronous APIs |
| PostgreSQL | Database to store users, signals, positions, and PnL |
| SQLAlchemy ORM | Maps Python models to database tables |
| Alembic | Handles database schema migrations |
| Pydantic | Input validation and response serialization |
| CCXT | Connects to Binance Testnet for live prices and simulated trades |
|Asyncio + Threading | Runs background position monitoring loops |
| Redis (Optional) | For caching and task coordination (future scope) |
| Python Logging | Structured log management for monitoring and debugging |

---

System Architecture


Frontend (React) ───► FastAPI Backend (Port 8000)
│
├── routes/ (REST endpoints)
├── services/ (Binance broker, monitor)
├── models/ (ORM models)
└── PostgreSQL Database

```

The backend performs:
1. Signal ingestion → via `/signals/update_active`
2. Signal approval → executes order on Binance
3. Position tracking → background monitor checks SL/TP
4. PnL updates → daily and per-position profit/loss tracking

---
Project Structure

```

app/
┣ routes/
┃ ┣ auth.py              # JWT-based authentication
┃ ┣ signals.py           # Signal approval/rejection and order creation
┃ ┣ positions.py         # Fetch open/closed positions
┃ ┣ orders.py            # Order management and status
┃ ┣ pnl.py               # Profit/Loss tracking
┃ ┣ risk.py              # Risk settings per user
┃ ┣ trade.py             # Manual trading APIs
┃ ┣ health.py            # Health check endpoint
┃ ┗ binance_test.py      # Binance Testnet connectivity check
┣ services/
┃ ┣ broker.py            # Core trading logic (BinanceBroker)
┃ ┣ monitor.py           # Background SL/TP monitoring loop
┃ ┗ strategy_engine.py   # Strategy logic integration (EMA-RSI etc.)
┣ models/
┃ ┣ signal_bd.py         # Signal model
┃ ┣ position.py          # Position lifecycle tracking
┃ ┣ order.py             # Orders table
┃ ┣ daily_pnl.py         # Daily aggregated PnL
┃ ┣ user.py              # User model for authentication
┃ ┗ audit_log.py         # Logs signal approval/rejection history
┣ utils/
┃ ┗ helpers.py           # Safe JSON serialization, rounding utilities
┣ database.py             # SQLAlchemy engine & session config
┣ logger.py               # Logging middleware
┣ main.py                 # App entrypoint & background task setup
┗ config.py               # Environment configuration (keys, URLs)

```

---

 Key Functionalities
 Signal Approval & Order Placement
- Converts “LONG”/“SHORT” → “BUY”/“SELL”.
- Adjusts quantity based on minimum notional value ($10).
- Applies symbol-specific step size (e.g., BTC = 0.0001).
- Places simulated order on Binance Testnet.
- Creates entries in `orders` and `positions` tables.
- Marks the signal as APPROVED and logs in `audit_log`.

 Open & Close Positions
- Position created immediately after signal approval.
- Background monitor checks live price every 10 seconds.
- Automatically closes position if SL/TP is hit.
- Updates DB: `exit_price`, `closed_at`, `status='CLOSED'`.
- Computes realized PnL and logs in `daily_pnl`.

 Manual Close Option
- User can manually stop any position via frontend.
- System closes it gracefully, tagging `reason='USER_STOPPED'`.
PnL Calculation
```

PnL = (Exit_Price - Entry_Price) * Quantity * (+1 for BUY / -1 for SELL)

````
Daily realized profits are aggregated in `daily_pnl`.

---

Background Monitor (app/services/monitor.py)

The monitor runs automatically at startup:
```python
@app.on_event("startup")
def start_background_tasks():
    threading.Thread(target=start_monitor_loop, daemon=True).start()
````

 Responsibilities:

* Fetch all open positions (`status='OPEN'`).
* Get live prices from Binance every 10s.
* Compare with SL and TP.
* Auto-close positions and record PnL.
Runs independently from FastAPI server, non-blocking.
Ensures 24/7 risk management automation.

---

Binance Integration

Binance Testnet is used for safe order execution during development.

| Function                      | Description                      |
| ----------------------------- | -------------------------------- |
| `get_quote(symbol)`           | Fetches live last-traded price   |
| `place_order(user_id, order)` | Places simulated market order    |
| `cancel_order(order_id)`      | Cancels active Binance order     |
| `close_position()`            | Updates DB and logs realized PnL |

API Security:
All requests are signed using HMAC-SHA256 and API keys stored in `.env`.

---

Authentication

Endpoints are secured via JWT.

Routes:

 `POST /auth/register` → Create new account
 `POST /auth/token` → Login & get JWT access token
 Protected routes include: `/signals`, `/positions`, `/pnl`

---

 Database Tables

| Table       | Purpose                                      |
| ----------- | -------------------------------------------- |
| `users`     | Authenticated platform users                 |
| `signals`   | Generated strategy signals (EMA-RSI outputs) |
| `orders`    | Placed Binance orders                        |
| `positions` | Active/closed trades                         |
| `daily_pnl` | Aggregated daily profit/loss                 |
| `audit_log` | Logs approvals, rejections, and closures     |

---

Environment Variables (`.env`)

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/trading_db
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_secret
REDIS_URL=redis://localhost:6379
```

---

Setup Instructions

Clone the repo

```bash
git clone https://github.com/yourusername/trading-bot-backend.git
cd trading-bot-backend
```

Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate (Windows)
```

Install dependencies

```bash
pip install -r requirements.txt
```

Setup environment

Create `.env` file and fill in your credentials (see above).

Run database migrations

```bash
alembic upgrade head
```

Run the FastAPI server

```bash
uvicorn app.main:app --reload
```

Server will start at:

```
http://127.0.0.1:8000
```

Start Frontend (React)

Frontend runs on port (3000) and communicates with backend at (8000)

---

 Example Workflow

 Strategy script (`run_stage4.py`) sends signals via `/signals/update_active`.
 User approves signal → backend executes trade on Binance.
 Position status set to `OPEN`.
 Background monitor auto-closes when SL/TP hit.
 Daily realized PnL updated in `daily_pnl`.
 Frontend displays live stats.

---

 Example Log Output

```
Signal 12 side converted to BUY
 Order placed for BTC/USDT | Binance ID: 123456
 Position 8 created as OPEN in DB
2025-10-31 12:12:10 | INFO | Found 1 open positions.
2025-10-31 12:12:20 | INFO | BTCUSDT | Current: 61200 | SL: 60800 | TP: 62200
 Position 8 closed at 62200 |
```

---

Future Enhancements

 Support for per-user Binance API keys
 Redis-based live PnL caching
 WebSocket live ticker integration
 Advanced risk control (max daily loss auto-freeze)
 Multi-strategy support (EMA-RSI, MACD, Supertrend)



> “Trade automation isn’t about predicting the market — it’s about eliminating emotion with disciplined execution.”


 
