from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class ApprovalAction(enum.Enum):
    approve = "approve"
    reject = "reject"


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(Enum(ApprovalAction), nullable=False)
    reason = Column(String, nullable=True)
    ts = Column(DateTime, default=datetime.utcnow)

    # Relationships (optional but useful for ORM navigation)
    signal = relationship("Signal", backref="approvals")
    user = relationship("User", backref="approvals")
