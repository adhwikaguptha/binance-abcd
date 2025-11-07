from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class SignalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    executed = "executed"
    expired = "expired"
    canceled = "canceled"

class SignalOut(BaseModel):
    id: int
    symbol: str
    side: str
    entry: float
    sl: float
    tp: Optional[float] = None
    qty: Optional[float] = None        # ✅ make optional
    ttl_sec: Optional[int] = None      # ✅ make optional
    status: SignalStatus
    created_at: datetime
    ts: datetime

    class Config:
        orm_mode = True
