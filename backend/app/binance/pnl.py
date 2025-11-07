from app.models.order import Order, OrderStatus
from app.database import SessionLocal

def calculate_realized_pnl():
    db = SessionLocal()
    filled = db.query(Order).filter(Order.status == OrderStatus.filled).all()
    total = 0
    for o in filled:
        total += (float(o.price) - float(o.price)) * float(o.qty)
    db.close()
    print(f"💰 Total PnL: {total:.4f}")
