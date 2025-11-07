# app/services/broker.py
from abc import ABC, abstractmethod
import asyncio
import requests
import redis
from sqlalchemy.orm import Session
from datetime import datetime, date
import json
import time
import hmac
import hashlib
from typing import Dict, Any
from decimal import Decimal

from app.models.order import Order, OrderStatus
from app.models.position import Position
from app.models.execution import Execution
from app.models.daily_pnl import DailyPnl
from app.models.audit_log import AuditLog
from app.config import settings

BINANCE_API_KEY = settings.BINANCE_API_KEY
BINANCE_API_SECRET = settings.BINANCE_API_SECRET
BINANCE_BASE_URL = "https://testnet.binance.vision/api/v3"


# -------------------------------
# Signing Helper (HMAC)
# -------------------------------
def sign_params(payload: dict) -> dict:
    items = sorted(payload.items())
    query = "&".join([f"{k}={v}" for k, v in items])
    signature = hmac.new(
        BINANCE_API_SECRET.encode("utf-8"),
        query.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    payload_with_sig = dict(payload)
    payload_with_sig["signature"] = signature
    return payload_with_sig


# -------------------------------
# Symbol helper
# -------------------------------
def clean_symbol(symbol: str) -> str:
    if not symbol:
        return symbol
    return "".join(ch for ch in symbol if ch.isalnum()).upper()


# -------------------------------
# Abstract Broker
# -------------------------------
class BrokerAdapter(ABC):
    @abstractmethod
    async def get_quote(self, symbol: str) -> dict: ...
    
    @abstractmethod
    async def place_order(self, user_id: int, order: dict) -> dict: ...
    
    @abstractmethod
    async def cancel_order(self, user_id: int, order_id: str) -> dict: ...
    
    @abstractmethod
    async def positions(self, user_id: int = None) -> list: ...


# -------------------------------
# Binance Broker
# -------------------------------
class BinanceBroker(BrokerAdapter):
    """Binance Testnet broker."""

    def __init__(self, db: Session = None):
        self.db = db
        try:
            self.redis = redis.Redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None
        except Exception:
            self.redis = None

    # ------------------------
    # Fetch live quote
    # ------------------------
    async def get_quote(self, symbol: str) -> dict:
        try:
            cleaned = clean_symbol(symbol)
            url = f"{BINANCE_BASE_URL}/ticker/price"
            resp = await asyncio.get_event_loop().run_in_executor(
                None, lambda: requests.get(url, params={"symbol": cleaned}, timeout=10)
            )
            resp.raise_for_status()
            data = resp.json()
            return {"last": float(data.get("price", 0.0)), "ts": datetime.utcnow().isoformat()}
        except Exception as e:
            return {"last": 0.0, "ts": datetime.utcnow().isoformat(), "error": str(e)}

    # ------------------------
    # Place order
    # ------------------------
    async def place_order(self, user_id: int, order: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from app.binance.client import place_order as binance_place_order

            cleaned_symbol = clean_symbol(order.get("symbol") or "")
            side = (order.get("side") or "").upper()
            if side not in ("BUY", "SELL"):
                raise ValueError(f"Invalid side: {order.get('side')}")

            raw_qty = order.get("qty")
            try:
                qty = float(raw_qty) if raw_qty is not None else None
            except (ValueError, TypeError):
                qty = None

            if not qty:
                qty = float(order.get("default_qty", 0.001) or 0.001)

            order_type = order.get("order_type", "MARKET")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: binance_place_order(
                    symbol=cleaned_symbol,
                    side=side,
                    qty=qty,
                    order_type=order_type
                )
            )

            if not result or "orderId" not in result:
                raise Exception("Binance rejected order or returned empty result")

            price = None
            try:
                fills = result.get("fills", [])
                if fills and isinstance(fills, list) and len(fills) > 0:
                    price = float(fills[0].get("price") or 0.0)
            except Exception:
                price = None

            if not price:
                price = float(order.get("entry") or 0.0)

            return {
                "orderId": result.get("orderId"),
                "symbol": cleaned_symbol,
                "side": side,
                "qty": qty,
                "price": price,
                "status": result.get("status", "NEW"),
                "raw": result
            }

        except Exception as e:
            raise Exception(f"Binance order placement failed: {str(e)}")

    # ------------------------
    # Cancel order
    # ------------------------
    async def cancel_order(self, user_id: int, order_id: str) -> dict:
        try:
            ts = int(time.time() * 1000)
            payload = {"orderId": order_id, "timestamp": ts}
            signed = sign_params(payload)
            headers = {"X-MBX-APIKEY": BINANCE_API_KEY} if BINANCE_API_KEY else {}
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.delete(f"{BINANCE_BASE_URL}/order", headers=headers, params=signed, timeout=10)
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    # ------------------------
    # Fetch open positions
    # ------------------------
    async def positions(self, user_id: int = None) -> list:
        query = self.db.query(Position).filter(Position.status == "OPEN")
        if user_id is not None:
            query = query.filter(Position.user_id == user_id)
        return query.all()

    # ------------------------
    # Close position
    # ------------------------
    async def close_position(self, position: Position, close_price: float, reason: str):
        execution = Execution(
            order_id=position.order_id,
            fill_price=close_price,
            qty=position.qty,
            ts=datetime.utcnow(),
        )
        self.db.add(execution)

        position.status = "CLOSED"
        position.closed_at = datetime.utcnow()
        position.exit_price = close_price

        avg_price = float(position.avg_price)
        qty = float(position.qty)
        if position.side.upper() == "BUY":
            pnl = (close_price - avg_price) * qty
        else:
            pnl = (avg_price - close_price) * qty

        daily_pnl = self.db.query(DailyPnl).filter(
            DailyPnl.user_id == position.user_id,
            DailyPnl.date == date.today(),
        ).first()

        if not daily_pnl:
            daily_pnl = DailyPnl(
                user_id=position.user_id,
                date=date.today(),
                realized=0.0,
                unrealized=0.0,
                max_dd=0.0,
            )
            self.db.add(daily_pnl)


        daily_pnl.realized = (daily_pnl.realized or Decimal(0)) + Decimal(str(pnl))

        daily_pnl.max_dd = min(daily_pnl.max_dd or 0, daily_pnl.realized)

        self.db.add(AuditLog(
            who=str(position.user_id),
            what="POSITION_CLOSED",
            payload_json=json.dumps({
                "symbol": position.symbol,
                "reason": reason,
                "pnl": float(pnl),
                "close_price": float(close_price),
                "timestamp": datetime.utcnow().isoformat()
            })
        ))

        self.db.commit()
        print(f"✅ Position {position.id} closed at {close_price} | PnL: {pnl:.2f}")
