# app/binance/client.py
import hmac
import hashlib
import time
import requests
import httpx

from app.config import settings

# === Binance Testnet Configuration ===
BINANCE_API_KEY = settings.BINANCE_API_KEY
BINANCE_API_SECRET = settings.BINANCE_API_SECRET
BASE_URL = "https://testnet.binance.vision/api/v3"  # SPOT TESTNET


def _sign_payload(payload: dict) -> dict:
    """Signs parameters using Binance HMAC-SHA256 signature"""
    query = "&".join([f"{k}={v}" for k, v in payload.items()])
    signature = hmac.new(
        BINANCE_API_SECRET.encode("utf-8"),
        query.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    payload["signature"] = signature
    return payload


def place_order(symbol: str, side: str, qty: float, order_type: str = "MARKET"):
    """
    Places a MARKET order on Binance Testnet.
    Returns response JSON if successful, or raises an Exception.
    """
    try:
        url = f"{BASE_URL}/order"
        timestamp = int(time.time() * 1000)

        payload = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type,
            "quantity": qty,
            "timestamp": timestamp,
        }

        signed = _sign_payload(payload)
        headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
        response = requests.post(url, headers=headers, params=signed)

        if response.status_code != 200:
            raise Exception(f"Binance API error {response.status_code}: {response.text}")

        return response.json()

    except Exception as e:
        print(f"[ERROR] Binance order placement failed: {str(e)}")
        return None


async def get_current_price(symbol: str) -> float:
    """
    Fetches the current market price for a symbol from Binance Testnet.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/ticker/price", params={"symbol": symbol.upper()})
            data = resp.json()
            return float(data["price"])
    except Exception as e:
        print(f"[ERROR] Failed to fetch price for {symbol}: {e}")
        return 0.0
