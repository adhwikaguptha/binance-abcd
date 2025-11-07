import threading
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import subprocess

# 🧩 Import all routers
from app.routes import (
    health,
    signals,
    positions,
    pnl,
    risk,
    trade,
    orders,
    auth,
    binance_test
)

# 🧠 Background monitor
from app.services.monitor import monitor_positions

# 🧾 Logging
from app.logger import setup_logging

# ✅ Load environment variables
load_dotenv()

# ✅ FastAPI instance
app = FastAPI(
    title="Trading Bot Backend",
    version="1.0",
    description="Paper trading bot backend with signal generation, risk control, and Binance testnet integration.",
)

# ------------------------
# CORS middleware
# ------------------------
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Logging middleware
setup_logging(app)

# ✅ Include all routers
routers = [
    health,
    signals,
    positions,
    pnl,
    risk,
    trade,
    orders,
    auth,
    binance_test
]

for r in routers:
    app.include_router(r.router)

# ✅ Root endpoint
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "🚀 Trading Bot API running successfully",
        "version": app.version,
    }

# ------------------------
# Background monitor thread
# ------------------------
def start_monitor_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor_positions())

@app.on_event("startup")
def start_background_tasks():
    """Starts position monitor in a separate thread to avoid blocking FastAPI."""
    # Start monitor
    t = threading.Thread(target=start_monitor_loop, daemon=True)
    t.start()

    # Start stage4 script as subprocess (optional)
    subprocess.Popen([
        "C:\\Users\\Admin\\Tradebot\\strategy\\venv\\Scripts\\python.exe",
        "C:\\Users\\Admin\\Tradebot\\strategy\\run_stage4.py"
    ])
