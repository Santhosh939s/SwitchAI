import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class ConversationCreateRequest(BaseModel):
    title: Optional[str] = "New Conversation"
    active_provider: Optional[str] = "anthropic"
    active_model: Optional[str] = None

class ConversationUpdateRequest(BaseModel):
    title: Optional[str] = None
    active_provider: Optional[str] = None
    active_model: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_role: str  # user, assistant
    content: str
    provider: Optional[str] = None
    model: Optional[str] = None
    latency_ms: Optional[float] = None
    token_estimate: Optional[int] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    active_provider: Optional[str] = None
    active_model: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class MessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    provider: Optional[str] = None
    model: Optional[str] = None
    web_search_enabled: Optional[bool] = False
    disable_rag_lookup: Optional[bool] = False
