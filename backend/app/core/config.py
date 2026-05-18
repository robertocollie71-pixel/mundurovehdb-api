from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    APP_NAME: str = "MunduroVehDB API"
    VERSION: str = "1.1"
    DEBUG: bool = True

    # === WAŻNE: wymuszamy SQLite ===
    DATABASE_URL: str = "sqlite+pysqlite:///./mundurovehdb.db"

    # Security
    SECRET_KEY: str = "super-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # MunduroVehDB specific
    ENCRYPTION_KEY: str = "SuperSecretEncryptionKey2026ForMunduroVehDB!"

@lru_cache()
def get_settings():
    return Settings()