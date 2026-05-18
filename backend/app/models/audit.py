from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from backend.app.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(36), nullable=False)
    user_id = Column(String(100), nullable=False)
    service = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    table_name = Column(String(50))
    record_id = Column(String(36))
    old_data = Column(JSON)
    new_data = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime, server_default=func.now())
