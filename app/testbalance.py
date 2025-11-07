import time, hmac, hashlib, requests, os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
BASE_URL = "https://testnet.binance.vision/api"

def sign(params: dict):
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    sig = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    return query + "&signature=" + sig

def get_account_info():
    ts = int(time.time() * 1000)
    params = {"timestamp": ts}
    url = f"{BASE_URL}/v3/account?{sign(params)}"
    r = requests.get(url, headers={"X-MBX-APIKEY": API_KEY})
    print(r.json())

get_account_info()
