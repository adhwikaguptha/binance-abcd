# app/routes/orders.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.dependencies import get_user_id  # safer, avoids 401

router = APIRouter(prefix="/orders", tags=["Orders"])


def to_float(value):
    """Safely convert Decimal or None to float."""
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


@router.get("/")
def get_user_orders(
    user_id: int = Depends(get_user_id),  # use same approach as positions.py
    db: Session = Depends(get_db)
):
    """
    Fetch orders from the database for the logged-in user only.
    """
    try:
        # ✅ Fetch only this user's orders
        orders = (
            db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.ts.desc())
            .all()
        )

        result = []
        for o in orders:
            result.append({
                "id": o.id,
                "user_id": o.user_id,
                "signal_id": o.signal_id,
                "side": o.side,
                "qty": to_float(o.qty),
                "price": to_float(o.price),
                "sl": to_float(o.sl),
                "tp": to_float(o.tp),
                "binance_order_id": o.binance_order_id,
                "status": o.status.value if hasattr(o.status, "value") else o.status,
                "ts": o.ts.isoformat() if o.ts else None,
            })

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")
