import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import OHLCV   # ✅ force import model

# Force table creation here
print("🔄 Creating tables if not exist...")
Base.metadata.create_all(bind=engine)
print("✅ Tables checked/created!")

# Binance CSV column mapping
COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume", "number_of_trades",
    "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
]

def parse_timestamp(raw):
    """Convert Binance timestamp to datetime, handling ms vs µs"""
    try:
        raw = float(raw)
        if raw > 1e15:   # microseconds
            return datetime.utcfromtimestamp(raw / 1_000_000)
        else:            # milliseconds
            return datetime.utcfromtimestamp(raw / 1000)
    except Exception as e:
        print(f"❌ Error parsing timestamp {raw}: {e}")
        return None

def load_csv_to_db(file_path, symbol="ETHUSDT", timeframe="1h"):
    df = pd.read_csv(file_path, header=None, names=COLUMNS)
    df["ts"] = df["open_time"].apply(parse_timestamp)

    db: Session = SessionLocal()
    try:
        records = []
        for _, row in df.iterrows():
            if row["ts"] is None:
                continue
            ohlcv = OHLCV(
                symbol=symbol,
                timeframe=timeframe,
                ts=row["ts"],
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"]
            )
            records.append(ohlcv)

        db.bulk_save_objects(records)
        db.commit()
        print(f"✅ Inserted {len(records)} OHLCV rows into DB for {symbol} ({timeframe})")

    except Exception as e:
        db.rollback()
        print("❌ Error inserting data:", e)

    finally:
        db.close()


if __name__ == "__main__":
    load_csv_to_db("C:\\Users\\Admin\\Downloads\\ETHUSDT-1h-2025-09-21\\ETHUSDT-1h-2025-09-21.csv", symbol="ETHUSDT", timeframe="1h")
