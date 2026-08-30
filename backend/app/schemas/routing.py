from pydantic import BaseModel, Field
from typing import Optional, List

class RoutingPreviewRequest(BaseModel):
    message: str = Field(..., min_length=1)
    priority: Optional[str] = "balanced"  # quality, speed, cost, balanced

class RoutingPreviewResponse(BaseModel):
    task_category: str  # general, coding, reasoning, long_context, summarization, creative, transformation, fast_response
    selected_provider: str
    selected_model: str
    rationale: str
    priority: str
    available_providers: List[str]
