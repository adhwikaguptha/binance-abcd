
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, ForeignKey
from app.database import Base
import enum
from datetime import datetime 

class OrderStatus(enum.Enum):
    NEW = "NEW"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REPLACED = "REPLACED"


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    signal_id = Column(Integer, ForeignKey("signals.id"))
    side = Column(String)
    qty = Column(Numeric)
    price = Column(Numeric)
    sl = Column(Numeric, nullable=True)
    tp = Column(Numeric, nullable=True)
    binance_order_id = Column(String, nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.NEW)
    ts = Column(DateTime, default=datetime.utcnow)
