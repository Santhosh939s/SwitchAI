import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class MemoryCreateRequest(BaseModel):
    category: str = Field(..., description="goal, fact, decision, constraint, preference, project_context, unresolved_question, task_state")
    key: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)
    is_pinned: bool = False

class MemoryUpdateRequest(BaseModel):
    category: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    is_pinned: Optional[bool] = None

class MemoryResponse(BaseModel):
    id: str
    conversation_id: str
    category: str
    key: str
    value: str
    is_pinned: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
