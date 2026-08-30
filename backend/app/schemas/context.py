from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class MessageItem(BaseModel):
    role: str
    content: str
    provider: Optional[str] = None
    model: Optional[str] = None

class MemoryItem(BaseModel):
    category: str
    key: str
    value: str
    is_pinned: bool = False

class FileContextItem(BaseModel):
    filename: str
    content_summary: str

class ContextPackage(BaseModel):
    conversation_id: str
    user_goal: Optional[str] = None
    summary: Optional[str] = None
    recent_messages: List[MessageItem] = Field(default_factory=list)
    relevant_memories: List[MemoryItem] = Field(default_factory=list)
    relevant_files: List[FileContextItem] = Field(default_factory=list)
    current_message: str
    constraints: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ContextPassportResponse(BaseModel):
    conversation_id: str
    user_goal: Optional[str] = None
    facts: List[str] = Field(default_factory=list)
    decisions: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    total_memories_transferred: int
    total_messages_transferred: int
    has_summary: bool
    active_provider: str
