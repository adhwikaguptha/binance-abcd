# app/models/signal_db.py

from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, Enum, ForeignKey, Index, Boolean
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime


# ✅ Enum for status
class SignalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EXPIRED = "expired"
    CANCELED = "canceled"


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)
    entry = Column(Numeric(18, 8), nullable=False)
    sl = Column(Numeric(18, 8), nullable=False)
    tp = Column(Numeric(18, 8))
    qty = Column(Numeric(18, 8))
    ttl_sec = Column(Integer)
    ctx_json = Column(String)

    status = Column(
        Enum(SignalStatus, name="signalstatus", values_callable=lambda e: [x.value for x in e]),
        default=SignalStatus.PENDING,
        nullable=False,
    )

    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    rejected_by = Column(Integer, ForeignKey("users.id"))
    rejected_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    ts = Column(DateTime, default=datetime.utcnow)

    payload_hash = Column(String)
    external_id = Column(String)
    source = Column(String, default="manual")

    # 🧩 NEW FIELDS for soft-delete & history tracking
    active = Column(Boolean, default=True, nullable=False)
    batch_id = Column(String, nullable=True, index=True)  # Optional grouping per 5-min batch

    strategy = relationship("Strategy", backref="signals", lazy="joined")

    __table_args__ = (
        Index("idx_signal_symbol_side", "symbol", "side"),
        Index("idx_signal_active", "active"),  # helps fast filtering
    )
