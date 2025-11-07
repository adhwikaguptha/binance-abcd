import time, hmac, hashlib, requests, os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

BASE_URL = "https://testnet.binance.vision/api/v3/account"

timestamp = int(time.time() * 1000)
query_string = f"timestamp={timestamp}&recvWindow=5000"
signature = hmac.new(
    BINANCE_API_SECRET.encode("utf-8"),
    query_string.encode("utf-8"),
    hashlib.sha256
).hexdigest()

headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
url = f"{BASE_URL}?{query_string}&signature={signature}"

print("📤 Sending:", url)
r = requests.get(url, headers=headers)
print("📥 Status:", r.status_code)
print("📥 Response:", r.text)
