from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from app.database import Base
from datetime import datetime 

class Execution(Base):
    __tablename__ = "executions"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    fill_price = Column(Numeric)
    qty = Column(Numeric)
    ts = Column(DateTime, default=datetime.utcnow)