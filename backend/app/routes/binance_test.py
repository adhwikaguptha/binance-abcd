# app/routes/binance_test.py
from fastapi import APIRouter, HTTPException
import requests, time, hmac, hashlib, os

router = APIRouter(prefix="/binance-test", tags=["Binance Test"])

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BASE_URL = "https://testnet.binance.vision/api/v3"

# ---- FIXED: do NOT crash backend if keys missing ----
if not BINANCE_API_KEY or not BINANCE_API_SECRET:
    print("⚠️ Warning: Binance API credentials missing. Test account endpoints will fail.")

def sign_params(params: dict) -> str:
    query_string = "&".join([f"{k}={params[k]}" for k in params])
    signature = hmac.new(
        (BINANCE_API_SECRET or "").encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return query_string + "&signature=" + signature


@router.get("/account")
def test_binance_connection():
    """
    Test Binance API /account (requires API key)
    """
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        raise HTTPException(status_code=400, detail="❌ API keys missing on server")

    try:
        ts = int(time.time() * 1000)
        params = {"timestamp": ts, "recvWindow": 5000}
        query = sign_params(params)

        url = f"{BASE_URL}/account?{query}"
        headers = {"X-MBX-APIKEY": BINANCE_API_KEY}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Binance test failed: {response.text}"
            )

        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Binance test failed: {str(e)}")


@router.get("/ping")
def ping_binance():
    """
    Simple ping (no API key needed)
    """
    try:
        url = "https://testnet.binance.vision/api/v3/ping"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "✅ Binance Testnet reachable",
                "status": response.status_code
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Binance Ping failed: {response.text}"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ping error: {str(e)}")
