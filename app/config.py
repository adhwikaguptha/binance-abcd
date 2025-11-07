from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Centralized configuration for your trading bot.
    Uses Pydantic v2 BaseSettings via `pydantic-settings`.
    """

    # === Database ===
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/trading_bot"
    REDIS_URL: str = "redis://localhost:6379/0"

    # === Binance Testnet ===
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    BINANCE_BASE_URL: str = "https://testnet.binance.vision"

    # === Auth / App ===
    ENV: str = "dev"
    JWT_SECRET: str = "supersecret"
    LOG_LEVEL: str = "INFO"
    DEBUG_MODE: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"  # ✅ Prevents “extra inputs not permitted” errors


settings = Settings()
