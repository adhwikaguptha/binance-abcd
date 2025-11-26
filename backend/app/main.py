import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import init_db

# Load environment variables
load_dotenv()

# ------------------------------------
# ✅ Create FastAPI app FIRST
# ------------------------------------
app = FastAPI(
    title="Trading Bot Backend",
    version="1.0",
    description="Trading bot backend with manual trigger for strategies.",
)

# ------------------------------------
# ✅ Startup event (MUST be after app)
# ------------------------------------
@app.on_event("startup")
def on_startup():
    init_db()
    print("🚀 Database initialized on startup")

# Routers
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

# Logging
from app.logger import setup_logging

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow Vercel + local
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
setup_logging(app)

# Include all routers
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

# Root endpoint
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "🚀 Backend running",
        "version": app.version,
    }

# Manual trigger endpoint (disabled for now)
from strategy.run_stage4 import run_strategy_once
@app.get("/run-strategy")
def run_strategy():
    try:
        return {"status": "success", "output": run_strategy_once()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
