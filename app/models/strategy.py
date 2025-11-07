from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Strategy(Base):
    __tablename__ = "strategies"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    name = Column(String, unique=True, index=True)
    params_json = Column(String)  # Store JSON as string
    enabled = Column(Boolean, default=True)