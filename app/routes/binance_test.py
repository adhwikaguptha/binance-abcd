# app/routes/binance_test.py
from fastapi import APIRouter, HTTPException
import requests, time, hmac, hashlib, os
from dotenv import load_dotenv

router = APIRouter(prefix="/binance-test", tags=["Binance Test"])

# Load environment variables
load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BASE_URL = "https://testnet.binance.vision/api/v3"

if not BINANCE_API_KEY or not BINANCE_API_SECRET:
    raise RuntimeError("❌ Missing Binance API credentials in .env file")


def sign_params(params: dict) -> str:
    """
    Sign parameters for Binance requests
    """
    query_string = "&".join([f"{k}={params[k]}" for k in params])
    signature = hmac.new(
        BINANCE_API_SECRET.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return query_string + "&signature=" + signature


@router.get("/account")
def test_binance_connection():
    """
    Test Binance API connection using /api/v3/account
    """
    try:
        ts = int(time.time() * 1000)
        params = {"timestamp": ts, "recvWindow": 5000}
        query = sign_params(params)

        url = f"{BASE_URL}/account?{query}"
        headers = {"X-MBX-APIKEY": BINANCE_API_KEY}

        print(f"📤 Sending: {url}")
        response = requests.get(url, headers=headers)

        print(f"📥 Status: {response.status_code}")
        print(f"📥 Raw Response: {response.text[:500]}")  # only preview first 500 chars

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Binance test failed: {response.text}"
            )

        # ✅ parse JSON safely
        try:
            return response.json()
        except Exception:
            raise HTTPException(status_code=500, detail="Binance returned non-JSON response")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Binance test failed: {str(e)}")
    
@router.get("/ping")
def ping_binance():
    """
    🔹 Simple ping to Binance Testnet API (no authentication required).
    Used for health checks and uptime monitoring.
    """
    try:
        url = "https://testnet.binance.vision/api/v3/ping"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "✅ Binance Testnet is reachable",
                "status_code": response.status_code
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Binance Ping failed: {response.text}"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ping error: {str(e)}")

