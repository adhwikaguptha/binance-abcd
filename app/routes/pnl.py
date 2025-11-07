from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Optional

import requests

from app.database import get_db
from app.models.daily_pnl import DailyPnl
from app.models.position import Position
from app.dependencies import get_user_id

router = APIRouter(prefix="/pnl", tags=["PnL"])

BINANCE_BASE_URL = "https://testnet.binance.vision/api/v3"


# ✅ 1️⃣ Live PnL (Today's realized + unrealized)
@router.get("/today")
async def get_today_pnl(
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    ✅ Returns today's Profit & Loss (PnL):
        - realized: from DailyPnl table
        - unrealized: calculated live from Binance testnet prices
        - max_dd: from DB (max drawdown)
    """
    daily_pnl = (
        db.query(DailyPnl)
        .filter(DailyPnl.user_id == user_id, DailyPnl.date == date.today())
        .first()
    )
    realized = float(daily_pnl.realized) if daily_pnl and daily_pnl.realized else 0.0
    max_dd = float(daily_pnl.max_dd) if daily_pnl and daily_pnl.max_dd else 0.0

    # Get open positions for live unrealized
    positions = db.query(Position).filter(
        Position.user_id == user_id, Position.status == "OPEN"
    ).all()

    unrealized_total = 0.0

    for pos in positions:
        symbol = pos.symbol.upper()
        qty = float(pos.qty)
        entry = float(pos.avg_price)

        try:
            resp = requests.get(f"{BINANCE_BASE_URL}/ticker/price", params={"symbol": symbol})
            data = resp.json()
            current_price = float(data.get("price", 0))

            if pos.side.upper() == "BUY":
                pnl = (current_price - entry) * qty
            else:
                pnl = (entry - current_price) * qty

            unrealized_total += pnl

        except Exception as e:
            print(f"[WARN] Could not fetch price for {symbol}: {e}")

    return {
        "date": date.today().isoformat(),
        "realized": round(realized, 2),
        "unrealized": round(unrealized_total, 2),
        "max_drawdown": round(max_dd, 2),
        "total_pnl": round(realized + unrealized_total, 2)
    }


# ✅ 2️⃣ Historical Summary PnL (last X days)
@router.get("/summary")
def get_pnl_summary(
    days: Optional[int] = 7,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    Returns total realized PnL for the user over the past X days (default = 7).
    Example: GET /pnl/summary?days=30
    """
    try:
        start_date = date.today() - timedelta(days=days)
        records = (
            db.query(DailyPnl)
            .filter(DailyPnl.user_id == user_id, DailyPnl.date >= start_date)
            .order_by(DailyPnl.date.asc())
            .all()
        )

        if not records:
            return {"message": "No PnL records found for this user."}

        total_pnl = sum(r.realized for r in records)

        return {
            "user_id": user_id,
            "days": days,
            "total_realized_pnl": round(total_pnl, 4),
            "daily_breakdown": [
                {
                    "date": r.date.isoformat(),
                    "realized": round(r.realized, 4),
                    "unrealized": round(r.unrealized or 0, 4),
                    "max_drawdown": round(r.max_dd or 0, 4),
                }
                for r in records
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch PnL summary: {str(e)}")
