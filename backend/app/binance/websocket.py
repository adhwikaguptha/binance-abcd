import json, requests, websockets, asyncio, os
from app.database import SessionLocal
from app.models.order import Order, OrderStatus

BASE_URL = os.getenv("BINANCE_BASE_URL", "https://testnet.binance.vision")
WS_BASE = "wss://testnet.binance.vision/ws"
API_KEY = os.getenv("BINANCE_API_KEY")

async def listen_order_updates():
    r = requests.post(f"{BASE_URL}/api/v3/userDataStream", headers={"X-MBX-APIKEY": API_KEY})
    listenKey = r.json()["listenKey"]
    ws_url = f"{WS_BASE}/{listenKey}"
    print(f"🔗 Listening to WebSocket: {ws_url}")

    async with websockets.connect(ws_url) as ws:
        async for msg in ws:
            data = json.loads(msg)
            if data.get("e") == "ORDER_TRADE_UPDATE":
                update = data["o"]
                db = SessionLocal()
                order = db.query(Order).filter(Order.id == update["i"]).first()
                if order:
                    order.status = update["X"]
                    order.price = float(update.get("L") or order.price)
                    db.commit()
                db.close()
