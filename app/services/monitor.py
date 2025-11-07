import asyncio
import logging
from datetime import datetime
from app.database import SessionLocal
from app.models.position import Position
from app.services.broker import BinanceBroker

# -------------------------------
# Logging configuration
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# -------------------------------
# Monitor function
# -------------------------------
async def monitor_positions():
    """
    Background task to monitor open positions:
    - Prints live prices
    - Tracks SL/TP
    - Updates exit_price/closed_at when closed
    Runs every 10 seconds.
    """
    while True:
        db = SessionLocal()
        try:
            broker = BinanceBroker(db)
            open_positions = await broker.positions(user_id=None)  # fetch all users
            logging.info(f"Found {len(open_positions)} open positions.")

            for pos in open_positions:
                db.refresh(pos)
                symbol = pos.symbol.replace("/", "")
                quote = await broker.get_quote(symbol)
                current_price = quote.get("last", 0.0)

                # Print live position info
                logging.info(
                    f"📌 {symbol} | Side: {pos.side} | Qty: {pos.qty} | "
                    f"Entry: {pos.avg_price:.4f} | SL: {pos.sl:.4f} | TP: {pos.tp:.4f} | Current: {current_price:.4f}"
                )

                # Check SL/TP and close position if hit
                if (pos.side.upper() == "BUY" and current_price >= pos.tp) or \
                   (pos.side.upper() == "SELL" and current_price <= pos.tp):
                    await broker.close_position(pos, current_price, "TAKE_PROFIT")

                elif (pos.side.upper() == "BUY" and current_price <= pos.sl) or \
                     (pos.side.upper() == "SELL" and current_price >= pos.sl):
                    await broker.close_position(pos, current_price, "STOP_LOSS")

        except Exception as e:
            logging.error(f"[Monitor Error] {e}", exc_info=True)
        finally:
            db.close()

        await asyncio.sleep(10)
