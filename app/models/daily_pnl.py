from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey
from sqlalchemy.schema import Index
from app.database import Base

class DailyPnl(Base):
    __tablename__ = "daily_pnl"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    date = Column(Date, primary_key=True)
    realized = Column(Numeric, default=0)
    unrealized = Column(Numeric, default=0)
    max_dd = Column(Numeric, default=0)
    __table_args__ = (
        Index("idx_daily_pnl_user_date", "user_id", "date"),
    )