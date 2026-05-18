from fastapi import Request
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal
from backend.app.models.audit import AuditLog

async def audit_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    
    # Przechowujemy w request.state (dla endpointów)
    request.state.request_id = request_id
    request.state.user_id = getattr(request.state, "user_id", "anonymous")
    request.state.service = getattr(request.state, "service", "munduro")

    start_time = datetime.utcnow()
    response = await call_next(request)
    duration = (datetime.utcnow() - start_time).total_seconds() * 1000

    # Zapis do tabeli audit_log
    db: Session = SessionLocal()
    try:
        log = AuditLog(
            request_id=request_id,
            user_id=request.state.user_id,
            service=request.state.service,
            action=f"{request.method} {request.url.path}",
            table_name="vehicles",
            record_id=None,
            old_data=None,
            new_data=None,
            ip_address=request.client.host if request.client else None,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"[AUDIT ERROR] {e}")
    finally:
        db.close()

    return response