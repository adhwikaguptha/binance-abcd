import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import init_db

# Load environment variables
load_dotenv()

# ------------------------------------
# Create FastAPI app
# ------------------------------------
app = FastAPI(
    title="Trading Bot Backend",
    version="1.0",
    description="Trading bot backend with EMA+RSI auto signals.",
)

# ------------------------------------
# Startup
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
    allow_origins=["*"],  # allow Vercel, localhost, Railway
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
setup_logging(app)

# Include routers
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

# ------------------------------------
# Root endpoint
# ------------------------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "🚀 Backend running",
        "version": app.version,
    }

# ------------------------------------
# Manual strategy trigger
# ------------------------------------
from app.strategy.run_stage4 import run_strategy_once

@app.get("/run-strategy")
def run_strategy():
    try:
        output = run_strategy_once()
        return {"status": "success", "output": output}
    except Exception as e:
        return {"status": "error", "message": str(e)}
