from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime 

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    who = Column(String)  # user_id or system
    what = Column(String)  # e.g., SIGNAL_APPROVED
    payload_json = Column(String)
    ts = Column(DateTime, default=datetime.utcnow)