# app/routes/binance_test.py

from fastapi import APIRouter, HTTPException

import requests, time, hmac, hashlib, os



router = APIRouter(prefix="/binance-test", tags=["Binance Test"])



# Environment variables

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")

BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")



# MUCH more reliable than testnet.binance.vision

SPOT_TESTNET = "https://testnet.binance.vision/api/v3"

FUTURES_TESTNET = "https://testnet.binancefuture.com/fapi/v1"



# Warn but DO NOT crash backend

if not BINANCE_API_KEY or not BINANCE_API_SECRET:

    print("⚠ Binance API keys not found. /account test will fail.")





# -------------------------

# SIGNING FUNCTION

# -------------------------

def sign_params(params: dict) -> str:

    query = "&".join([f"{k}={params[k]}" for k in params])

    signature = hmac.new(

        (BINANCE_API_SECRET or "").encode(),

        query.encode(),

        hashlib.sha256

    ).hexdigest()

    return query + "&signature=" + signature





# -------------------------

# PING ENDPOINT (NO KEY)

# -------------------------

@router.get("/ping")

def ping_binance():

    """

    Pings Futures Testnet (most stable)

    """

    url = f"{FUTURES_TESTNET}/ping"



    try:

        response = requests.get(

            url,

            timeout=5,

            headers={"User-Agent": "Mozilla/5.0"}  # Cloudflare bypass

        )



        # OK response

        if response.status_code == 200:

            return {

                "success": True,

                "message": "✅ Binance Futures Testnet reachable",

                "status_code": 200

            }



        raise HTTPException(

            status_code=response.status_code,

            detail=f"Binance ping failed: {response.text}"

        )



    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Ping error: {str(e)}")





# -------------------------

# ACCOUNT CHECK (REQUIRES KEY)

# -------------------------

@router.get("/account")

def test_binance_connection():

    """

    Test authenticated account endpoint (requires API keys).

    """

    if not BINANCE_API_KEY or not BINANCE_API_SECRET:

        raise HTTPException(status_code=400, detail="❌ API keys missing on server")



    ts = int(time.time() * 1000)

    params = {"timestamp": ts, "recvWindow": 5000}

    signed = sign_params(params)



    url = f"{SPOT_TESTNET}/account?{signed}"



    try:

        response = requests.get(

            url,

            timeout=10,

            headers={

                "X-MBX-APIKEY": BINANCE_API_KEY,

                "User-Agent": "Mozilla/5.0"

            }

        )



        if response.status_code != 200:

            raise HTTPException(

                status_code=response.status_code,

                detail=f"Binance account test failed: {response.text}"

            )



        return response.json()



    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Binance test failed: {str(e)}")
