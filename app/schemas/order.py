from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrderOut(BaseModel):
    id: int
    user_id: int
    signal_id: int
    side: str
    qty: float
    price: float
    sl: Optional[float] = None
    tp: Optional[float] = None
    binance_order_id: Optional[str] = None
    status: str
    ts: datetime

    class Config:
        from_attributes = True  # ✅ allows Pydantic v2 to read from ORM models
