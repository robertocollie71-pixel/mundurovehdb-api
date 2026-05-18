import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import get_settings
from backend.app.routers.vehicles import router as vehicles_router
from backend.app.routers.external import router as external_router
from backend.app.models.base import Base
from backend.app.db.session import engine

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# === NAJPROSTSZY I NAJBARDZIEJ SKUTECZNY CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400
)

# === RĘCZNY PREFLIGHT – to jest klucz ===
@app.options("/external/citizens")
async def preflight_citizens(request: Request):
    print("=== [CORS] Obsłużono preflight OPTIONS /external/citizens ===")
    return {"status": "ok"}

@app.options("/external/{path:path}")
async def preflight_all(request: Request):
    print(f"=== [CORS] Obsłużono preflight OPTIONS /external/{request.path_params.get('path', '')} ===")
    return {"status": "ok"}

app.include_router(vehicles_router)
app.include_router(external_router)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("✅ Tabele SQLite gotowe")

@app.get("/health")
async def health():
    return {"status": "ok"}

print("=== main.py – GROK CODE FINAL v3 (ultra prosty CORS + dedykowany OPTIONS) ===")
