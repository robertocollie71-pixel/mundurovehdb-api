from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from backend.app.models.base import Base
from datetime import datetime, timedelta

class SMSVerification(Base):
    __tablename__ = "sms_verification"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), nullable=False, index=True)
    verification_code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    def is_valid(self):
        return not self.used and datetime.utcnow() < self.expires_at