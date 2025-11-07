from fastapi import HTTPException
from app.models.risk_settings import RiskSettings
from app.models.daily_pnl import DailyPnl
from datetime import date

class RiskEngine:
    def check_trade(self, db, user_id: int, signal: dict):
        settings = db.query(RiskSettings).filter(RiskSettings.user_id == user_id).first()
        if not settings:
            raise HTTPException(status_code=400, detail={"code": "NO_RISK_SETTINGS", "message": "Risk settings not found"})

        proposed_loss = abs(signal["entry"] - signal["sl"]) * signal["qty"]
        max_loss = settings.capital * settings.risk_per_trade_pct
        if proposed_loss > max_loss:
            raise HTTPException(status_code=400, detail={"code": "RISK_PER_TRADE_EXCEEDED", "message": f"Proposed loss {proposed_loss} > limit {max_loss}"})

        daily_pnl = db.query(DailyPnl).filter(DailyPnl.user_id == user_id, DailyPnl.date == date.today()).first()
        today_loss = daily_pnl.realized if daily_pnl else 0
        max_daily_loss = settings.capital * settings.max_daily_loss_pct
        if today_loss <= -max_daily_loss:
            raise HTTPException(status_code=400, detail={"code": "DAILY_LOSS_LIMIT_EXCEEDED", "message": "Daily loss limit reached"})
        return True