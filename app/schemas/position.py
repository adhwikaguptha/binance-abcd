from pydantic import BaseModel
from datetime import datetime

class PositionOut(BaseModel):
    id: int
    user_id: int
    symbol: str
    qty: float
    avg_price: float
    sl: float
    tp: float
    status: str
    opened_at: datetime
    unrealized_pnl: float

    class Config:
        orm_mode = True