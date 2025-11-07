# app/routes/trade_routes.py
from fastapi import APIRouter
from app.binance.services import create_order  # this calls your Binance order logic

router = APIRouter(prefix="/trade", tags=["Trade"])

@router.post("/")
def trade(symbol: str, user_id: int, signal_id: int, qty: float, side: str = "BUY"):
    """
    Place a trade on Binance Testnet and save it to DB.
    """
    return create_order(symbol, user_id, signal_id, qty, side)
