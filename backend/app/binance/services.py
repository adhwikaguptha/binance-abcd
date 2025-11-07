from app.binance.client import place_order
from app.binance.websocket import listen_order_updates
from app.models.order import Order, OrderStatus
from app.database import SessionLocal
from datetime import datetime
import asyncio

def create_order(symbol, user_id, signal_id, qty, side="BUY"):
    response = place_order(symbol, side, qty)
    if "orderId" not in response:
        print("❌ Order failed:", response)
        return None

    db = SessionLocal()
    order = Order(
        user_id=user_id,
        signal_id=signal_id,
        side=side,
        qty=float(response["origQty"]),
        price=float(response.get("price") or 0),
        status=OrderStatus.new,
        ts=datetime.utcnow()
    )
    db.add(order)
    db.commit()
    db.close()
    return response

async def run_listener():
    await listen_order_updates()
