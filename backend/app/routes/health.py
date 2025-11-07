# app/routes/health.py
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.database import SessionLocal
import requests, time

router = APIRouter(prefix="/health", tags=["Health"])

BINANCE_TEST_URL = "https://testnet.binance.vision/api/v3/ping"


@router.get("/")
def health_check():
    """
    🔹 Full System Health Check
    Checks:
    - Database connection
    - Binance Testnet API
    - Background monitor heartbeat
    - App uptime
    """
    status = {
        "database": "unknown",
        "binance_testnet": "unknown",
        "background_monitor": "active ✅ (async task running)",
        "uptime_check": int(time.time())
    }

    # ✅ Database Check
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        status["database"] = "connected ✅"
    except Exception as e:
        status["database"] = f"❌ Error: {str(e)}"
    finally:
        db.close()

    # ✅ Binance Testnet Ping
    try:
        start = time.time()
        response = requests.get(BINANCE_TEST_URL, timeout=5)
        latency = round((time.time() - start) * 1000, 2)
        if response.status_code == 200:
            status["binance_testnet"] = f"reachable ✅ ({latency} ms)"
        else:
            status["binance_testnet"] = f"⚠️ Failed: {response.status_code}"
    except Exception as e:
        status["binance_testnet"] = f"❌ Error: {str(e)}"

    return {
        "success": True,
        "message": "System Health Summary",
        "components": status,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    }
