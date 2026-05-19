# === MONKEY-PATCH pysqlite3 usunięty – używamy PostgreSQL ===

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.core.config import get_settings
from backend.app.middleware.audit import audit_middleware
from backend.app.routers.vehicles import router as vehicles_router
from backend.app.routers.external import router as external_router
from backend.app.models.base import Base
from backend.app.db.session import engine

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="MunduroVehDB – Faza 1.0",
)

# === AGRESYWNY CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Middleware audit (jeśli masz) ===
# app.middleware("http")(audit_middleware)

app.include_router(vehicles_router)
app.include_router(external_router)

# === Tworzenie tabel przy starcie ===
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    print("✅ Tabele PostgreSQL gotowe")

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.VERSION, "database": "PostgreSQL"}

print("=== main.py załadowany z PostgreSQL ===")
