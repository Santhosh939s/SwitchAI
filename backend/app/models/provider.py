import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from app.core.database import Base

class ProviderConnection(Base):
    __tablename__ = "provider_connections"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    provider_name = Column(String, nullable=False)  # anthropic, gemini, openai
    encrypted_api_key = Column(Text, nullable=False)
    status = Column(String, default="active")  # active, rate_limited, error, disconnected
    default_model = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
