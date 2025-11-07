from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Base class for models
Base = declarative_base()

# Create engine
engine = create_engine(settings.DATABASE_URL, echo=False, future=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
from sqlalchemy import event
from decimal import Decimal

@event.listens_for(SessionLocal, "before_flush")
def convert_decimal_before_flush(session, flush_context, instances):
    for instance in session.new.union(session.dirty):
        for attr in instance.__dict__:
            value = getattr(instance, attr)
            if isinstance(value, Decimal):
                setattr(instance, attr, float(value))

