import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from app.core.database import Base

class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    category = Column(String, nullable=False)  # goal, fact, decision, constraint, preference, project_context, unresolved_question
    key = Column(String, nullable=False)
    value = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
