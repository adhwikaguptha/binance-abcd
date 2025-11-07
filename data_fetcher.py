import ccxt
import asyncio
from app.database import SessionLocal
from app.models.ohlcv import OHLCV
from datetime import datetime

exchange = ccxt.binance({
    'apiKey': 'pTUzwvPZGwuNVDdGuPOYfM8oiP3Fjgg8eZl5IDhVPCjUimq5ZufYctorSSO7MuwD',  # Replace with your Binance testnet API key
    'secret': 'IS7Ws0uS8UJ37o2GfM7HCd3G5r7rPQuLx86ro5DICVh2QuRRmnKwvRa12ofWKVdk',   # Replace with your Binance testnet secret
    'enableRateLimit': True,
    'test': True  # Use testnet
})

async def fetch_and_store(symbol="BTC/USDT", timeframe="5m", limit=100):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    with SessionLocal() as db:
        for candle in ohlcv:
            db_ohlcv = OHLCV(
                symbol=symbol,
                timeframe=timeframe,
                ts=datetime.fromtimestamp(candle[0] / 1000),
                open=candle[1],
                high=candle[2],
                low=candle[3],
                close=candle[4],
                volume=candle[5]
            )
            db.add(db_ohlcv)
        db.commit()
    print(f"Fetched and stored {len(ohlcv)} candles for {symbol}")

async def run_fetcher():
    while True:
        await fetch_and_store()
        await asyncio.sleep(3600)  # Fetch every hour

if __name__ == "__main__":
    asyncio.run(run_fetcher())