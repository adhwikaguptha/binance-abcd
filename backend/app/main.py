import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import init_db

@app.on_event("startup")
def on_startup():
    init_db()

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

# Manual strategy imports
#from strategy.run_stage4 import run_strategy_once   # <-- modify path as needed

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI(
    title="Trading Bot Backend",
    version="1.0",
    description="Trading bot backend with manual trigger for strategies.",
)

# CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Allow all for Railway + Vercel
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


# =====================================================
# 🚀 MANUAL TRIGGER STRATEGY ENDPOINT
# =====================================================
#@app.get("/run-strategy")
#def run_strategy():
 #   """Runs trading strategy ONE TIME when called manually."""
  #  try:
   #     output = run_strategy_once()   # your function
    #    return {"status": "success", "output": output}
    #except Exception as e:
     #   return {"status": "error", "message": str(e)}
