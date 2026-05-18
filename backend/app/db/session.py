# === MONKEY-PATCH pysqlite3 ===
import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import get_settings

settings = get_settings()

# Warunkowe connect_args – tylko dla SQLite
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL.lower() else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
