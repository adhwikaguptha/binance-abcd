from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models.risk_settings import RiskSettings
from app.models.daily_pnl import DailyPnl
from app.schemas.risk import RiskOut
from app.dependencies import get_user_id

router = APIRouter(tags=["risk"])

# ------------------ GET: Fetch risk + daily PnL ------------------
@router.get("/risk", response_model=RiskOut)
async def get_risk_settings(user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    """Fetch current risk settings and today's PnL for user."""
    settings = db.query(RiskSettings).filter(RiskSettings.user_id == user_id).first()
    daily_pnl = db.query(DailyPnl).filter(DailyPnl.user_id == user_id, DailyPnl.date == date.today()).first()
    return RiskOut(
        capital=settings.capital if settings else 100000,
        risk_per_trade_pct=settings.risk_per_trade_pct if settings else 0.01,
        max_daily_loss_pct=settings.max_daily_loss_pct if settings else 0.02,
        today_loss=daily_pnl.realized if daily_pnl else 0
    )

# ------------------ POST: Create risk settings ------------------
@router.post("/risk/setup")
async def setup_risk_settings(
    capital: float,
    risk_per_trade_pct: float,
    max_daily_loss_pct: float,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    """Allow user to create their own risk settings."""
    existing = db.query(RiskSettings).filter(RiskSettings.user_id == user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Risk settings already exist for this user")

    new_settings = RiskSettings(
        user_id=user_id,
        capital=capital,
        risk_per_trade_pct=risk_per_trade_pct,
        max_daily_loss_pct=max_daily_loss_pct,
    )
    db.add(new_settings)
    db.commit()
    db.refresh(new_settings)
    return {"message": "Risk settings created successfully", "data": new_settings}

# ------------------ PUT: Update risk settings ------------------
@router.put("/risk/update")
async def update_risk_settings(
    capital: float,
    risk_per_trade_pct: float,
    max_daily_loss_pct: float,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    """Update an existing user's risk settings."""
    settings = db.query(RiskSettings).filter(RiskSettings.user_id == user_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="No risk settings found for this user")

    settings.capital = capital
    settings.risk_per_trade_pct = risk_per_trade_pct
    settings.max_daily_loss_pct = max_daily_loss_pct

    db.commit()
    db.refresh(settings)
    return {"message": "Risk settings updated successfully", "data": settings}
