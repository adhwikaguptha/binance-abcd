"""
Binance Testnet Order Tracking PoC (PostgreSQL version, auto-detect signal)
---------------------------------------------------------------------------
✅ Places a testnet order (MARKET)
✅ Saves order info into PostgreSQL (user_id + latest signal_id)
✅ Listens to ORDER_TRADE_UPDATE via WebSocket
✅ Updates DB on fills
✅ Computes realized PnL (basic)
"""

import asyncio
import time
import hmac
import hashlib
import json
import requests
import websockets
from urllib.parse import urlencode
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import os

# Import your models
from app.models.order import Order, OrderStatus  # <- path based on your backend
from app.models.singal_bd import Signal          # <- your Signal model file
from app.database import Base

# ====== CONFIG ======
load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
BASE_URL = os.getenv("BINANCE_BASE_URL", "https://testnet.binance.vision")
DATABASE_URL = os.getenv("DATABASE_URL")

WS_BASE = "wss://testnet.binance.vision/ws"
SYMBOL = "ETHUSDT"
QTY = 0.02
USER_ID = 1  # assuming demo user

# ====== DB SETUP ======
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


# ====== HELPERS ======
def sign_params(params):
    """Sign Binance request parameters"""
    query = urlencode(params)
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    return f"{query}&signature={signature}"


def get_latest_signal_id():
    """Automatically fetch the latest signal ID from DB"""
    db = SessionLocal()
    latest_signal = db.query(Signal).order_by(desc(Signal.id)).first()
    db.close()
    if latest_signal:
        print(f"🧩 Using latest signal ID: {latest_signal.id} ({latest_signal.symbol}, {latest_signal.side})")
        return latest_signal.id
    else:
        print("⚠️ No signal found in database — please insert one first.")
        return None


def place_order(symbol, side="BUY", qty=0.01, order_type="MARKET"):
    """Place an order on Binance Testnet"""
    latest_signal_id = get_latest_signal_id()
    if not latest_signal_id:
        print("❌ Cannot place order — no signal found.")
        return None

    url = f"{BASE_URL}/api/v3/order"
    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": qty,
        "timestamp": int(time.time() * 1000)
    }
    signed_query = sign_params(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    r = requests.post(url, data=signed_query, headers=headers)
    data = r.json()

    if r.status_code != 200:
        print("❌ Order Failed:", data)
        return None

    print("✅ Order placed:", data)

    # Save order in DB
    db = SessionLocal()
    order = Order(
        user_id=USER_ID,
        signal_id=latest_signal_id,  # ✅ auto-linked
        side=data["side"],
        qty=float(data["origQty"]),
        price=float(data.get("price") or 0),
        status=OrderStatus.new,
        ts=datetime.utcnow()
    )
    db.add(order)
    db.commit()
    db.close()
    return data


async def listen_order_updates():
    """Listen for ORDER_TRADE_UPDATE events via WebSocket"""
    # Step 1: Create listenKey
    r = requests.post(f"{BASE_URL}/api/v3/userDataStream", headers={"X-MBX-APIKEY": API_KEY})
    listenKey = r.json()["listenKey"]
    ws_url = f"{WS_BASE}/{listenKey}"
    print(f"🔗 Listening to WebSocket: {ws_url}")

    async with websockets.connect(ws_url) as ws:
        async for msg in ws:
            data = json.loads(msg)
            if data.get("e") == "ORDER_TRADE_UPDATE":
                order_update = data["o"]
                print(f"📩 ORDER UPDATE: {order_update['X']} @ {order_update.get('L')}")

                db = SessionLocal()
                order = db.query(Order).filter(Order.id == order_update["i"]).first()
                if order:
                    order.status = order_update["X"]  # e.g., NEW, FILLED, CANCELED
                    order.price = float(order_update.get("L") or order.price)
                    db.commit()
                db.close()


def calculate_realized_pnl():
    """Compute simple realized PnL for filled orders"""
    db = SessionLocal()
    filled_orders = db.query(Order).filter(Order.status == OrderStatus.filled).all()
    total_pnl = 0
    for order in filled_orders:
        pnl = float(order.qty) * (float(order.price) - float(order.price))
        total_pnl += pnl
    db.close()
    print(f"💰 Total Realized PnL: {total_pnl:.4f}")


async def main():
    print("🚀 Starting Binance Order Tracking (PostgreSQL version)...")

    # 1️⃣ Place test order
    order = place_order(SYMBOL, side="BUY", qty=QTY)
    if not order:
        return

    # 2️⃣ Start WebSocket listener
    ws_task = asyncio.create_task(listen_order_updates())

    # 3️⃣ Wait 60s for updates
    await asyncio.sleep(60)
    ws_task.cancel()

    # 4️⃣ Compute PnL
    calculate_realized_pnl()


if __name__ == "__main__":
    asyncio.run(main())
