from pydantic import BaseModel

class PnlOut(BaseModel):
    realized: float
    unrealized: float
    max_dd: float