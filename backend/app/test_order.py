import time
import hmac
import hashlib
import requests
import os
from dotenv import load_dotenv

# -------------------------------
# ✅ Load .env
# -------------------------------
load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
BASE_URL = "https://testnet.binance.vision/api"

# -------------------------------
# ✅ Sign params helper
# -------------------------------
def sign_params(params: dict) -> dict:
    query = "&".join([f"{k}={params[k]}" for k in params])
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    return params

# -------------------------------
# ✅ Place Market Order
# -------------------------------
def place_market_order(symbol: str, side: str, qty: float):
    ts = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,           # BUY or SELL
        "type": "MARKET",
        "quantity": qty,
        "timestamp": ts,
    }

    signed_params = sign_params(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    response = requests.post(f"{BASE_URL}/v3/order", headers=headers, params=signed_params)
    return response.json()

# -------------------------------
# ✅ Run test
# -------------------------------
if __name__ == "__main__":
    symbol = "ETHUSDT"    # You can change to BTCUSDT, BNBUSDT, etc.
    side = "BUY"
    qty = 0.01             # Small trade amount

    print(f"📤 Placing {side} order for {qty} {symbol} on Binance Testnet...\n")
    result = place_market_order(symbol, side, qty)

    print("✅ Binance Testnet response:")
    print(result)
