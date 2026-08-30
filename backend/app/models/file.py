import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from app.core.database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    extracted_text_context = Column(Text, nullable=True)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
