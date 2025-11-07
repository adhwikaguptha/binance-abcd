from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.position import Position
from datetime import datetime

# Create all tables if they don't exist
Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    # Check and add users (to avoid duplicates)
    new_users = [
        {"username": "cryptoFan", "email": "fan@crypto.com", "role": "trader", "password_hash": "hashed_secret1"},
        {"username": "tradePro", "email": "pro@trade.com", "role": "trader", "password_hash": "hashed_secret2"},
    ]
    for user_data in new_users:
        existing_user = db.query(User).filter_by(username=user_data["username"]).first()
        if not existing_user:
            new_user = User(**user_data)
            db.add(new_user)
            db.commit()  # Commit each to get the ID
        else:
            print(f"User {user_data['username']} already exists, skipping.")

    # Add positions
    positions = [
        Position(user_id=1, symbol="BTC/USDT", qty=0.5, avg_price=45000.00, sl=44000.00, tp=47000.00, state="open", opened_at=datetime(2025, 9, 21, 14, 0)),
        Position(user_id=2, symbol="ETH/USDT", qty=2.0, avg_price=3000.00, sl=2900.00, tp=3200.00, state="open", opened_at=datetime(2025, 9, 21, 14, 5)),
    ]
    db.add_all(positions)
    db.commit()
    print("Added some test positions!")