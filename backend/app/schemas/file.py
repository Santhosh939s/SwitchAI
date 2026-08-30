import datetime
from pydantic import BaseModel
from typing import Optional

class FileUploadResponse(BaseModel):
    id: str
    conversation_id: str
    filename: str
    file_type: str
    file_size: int
    extracted_text_summary: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True
