import time
import hmac
import hashlib
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# ✅ Spot Testnet credentials
# -----------------------------
API_KEY = os.environ.get("BINANCE_API_KEY")
API_SECRET = os.environ.get("BINANCE_API_SECRET")

# ✅ Spot Testnet base URL (NOT futures)
BASE_URL = "https://testnet.binance.vision/api"

# -----------------------------
# ✅ Helper: Sign requests
# -----------------------------
def sign_params(params: dict) -> str:
    query = "&".join([f"{k}={params[k]}" for k in params])
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    return query + "&signature=" + signature

# -----------------------------
# ✅ Get all orders
# -----------------------------
def get_all_orders(symbol: str):
    ts = int(time.time() * 1000)
    params = {"symbol": symbol, "timestamp": ts}
    url = f"{BASE_URL}/v3/allOrders?{sign_params(params)}"
    resp = requests.get(url, headers={"X-MBX-APIKEY": API_KEY})
    return resp.json()

# -----------------------------
# ✅ Get open orders
# -----------------------------
def get_open_orders(symbol: str):
    ts = int(time.time() * 1000)
    params = {"symbol": symbol, "timestamp": ts}
    url = f"{BASE_URL}/v3/openOrders?{sign_params(params)}"
    resp = requests.get(url, headers={"X-MBX-APIKEY": API_KEY})
    return resp.json()

# -----------------------------
# ✅ Get my trades
# -----------------------------
def get_my_trades(symbol: str):
    ts = int(time.time() * 1000)
    params = {"symbol": symbol, "timestamp": ts}
    url = f"{BASE_URL}/v3/myTrades?{sign_params(params)}"
    resp = requests.get(url, headers={"X-MBX-APIKEY": API_KEY})
    return resp.json()

# -----------------------------
# ✅ Example usage
# -----------------------------
if __name__ == "__main__":
    symbol = "ETHUSDT"

    print("=== All Orders ===")
    print(get_all_orders(symbol))

    print("\n=== Open Orders ===")
    print(get_open_orders(symbol))

    print("\n=== My Trades ===")
    print(get_my_trades(symbol))
