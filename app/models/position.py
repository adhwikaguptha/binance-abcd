
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, ForeignKey
from app.database import Base
from sqlalchemy.schema import Index
from datetime import datetime
import enum

class PositionState(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    symbol = Column(String, nullable=False)
    qty = Column(Numeric, nullable=False)
    avg_price = Column(Numeric, nullable=False)
    sl = Column(Numeric, nullable=False)
    tp = Column(Numeric, nullable=False)
    side = Column(String, nullable=False)
    status = Column(Enum(PositionState), default=PositionState.OPEN)
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    exit_price = Column(Numeric, nullable=True)

    __table_args__ = (
        Index("idx_position_user_symbol", "user_id", "symbol"),
    ) 