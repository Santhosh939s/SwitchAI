import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Boolean, Text
from app.core.database import Base

class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    is_success = Column(Boolean, default=True)
    latency_ms = Column(Float, nullable=False)
    estimated_tokens = Column(Integer, default=0)
    is_fallback = Column(Boolean, default=False)
    error_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ProviderEvent(Base):
    __tablename__ = "provider_events"

    id = Column(String, primary_key=True, index=True)
    provider = Column(String, nullable=False)
    status_code = Column(Integer, nullable=True)
    error_type = Column(String, nullable=True)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
