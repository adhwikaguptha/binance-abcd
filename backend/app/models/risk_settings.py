from sqlalchemy import Column, Integer, Numeric, ForeignKey
from app.database import Base

class RiskSettings(Base):
    __tablename__ = "risk_settings"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    capital = Column(Numeric, default=100000)
    risk_per_trade_pct = Column(Numeric, default=0.01)  # 1%
    max_daily_loss_pct = Column(Numeric, default=0.02)  # 2%