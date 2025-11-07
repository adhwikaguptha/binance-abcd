from pydantic import BaseModel

class RiskOut(BaseModel):
    capital: float
    risk_per_trade_pct: float
    max_daily_loss_pct: float
    today_loss: float