from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.position import Position
from app.dependencies import get_user_id
from datetime import datetime

router = APIRouter(tags=["positions"])


def to_float(value):
    """Safely convert Decimal or None to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_iso(value):
    """Convert datetime to ISO string for frontend."""
    if isinstance(value, datetime):
        return value.isoformat()
    return None


@router.get("/positions")
async def get_positions(user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    positions = db.query(Position).filter(Position.user_id == user_id).all()

    result = []
    for pos in positions:
        result.append({
            "id": pos.id,  # ✅ add unique key for React
            "symbol": pos.symbol,
            "side": pos.side,
            "order_id": pos.order_id,
            "qty": to_float(pos.qty),
            "avg_price": to_float(pos.avg_price),
            "sl": to_float(pos.sl),
            "tp": to_float(pos.tp),
            "status": pos.status,
            "exit_price": to_float(pos.exit_price),
            "opened_at": to_iso(pos.opened_at),
            "closed_at": to_iso(pos.closed_at),
            "pnl": round((to_float(pos.avg_price or 0) - 2500.0) * to_float(pos.qty or 0), 2),  # example calc
        })

    return result
