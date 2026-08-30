import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Float
from app.core.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    sender_role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    provider = Column(String, nullable=True)
    model = Column(String, nullable=True)
    latency_ms = Column(Float, nullable=True)
    token_estimate = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
