# app/routes/binance_debug.py
from fastapi import APIRouter, Depends, HTTPException
import time, hmac, hashlib, requests, os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(tags=["binance-debug"])

BASE_URL = "https://testnet.binance.vision/api"
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")


def sign_params(params: dict) -> str:
    """Helper to sign Binance requests"""
    query = "&".join([f"{k}={params[k]}" for k in params])
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    return query + "&signature=" + signature


@router.get("/binance/orders")
def get_binance_orders(symbol: str = "ETHUSDT"):
    """🔍 Debug endpoint: Get your live Binance testnet orders"""
    try:
        ts = int(time.time() * 1000)
        params = {"symbol": symbol, "timestamp": ts}
        query = sign_params(params)
        url = f"{BASE_URL}/v3/allOrders?{query}"

        resp = requests.get(url, headers={"X-MBX-APIKEY": API_KEY})
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 