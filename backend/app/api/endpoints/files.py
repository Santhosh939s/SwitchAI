import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.file import File
from app.schemas.file import FileUploadResponse

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    conversation_id: str = Form(...),
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()
        file_size = len(content)
        
        if file_size > 5 * 1024 * 1024:  # 5 MB limit
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds 5MB limit")

        text_content = ""
        try:
            text_content = content.decode("utf-8")
        except Exception:
            text_content = f"Binary file attachment: {file.filename}"

        summary = text_content[:500] if text_content else f"Attached file: {file.filename}"

        db_file = File(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            filename=file.filename or "uploaded_file.txt",
            file_type=file.content_type or "text/plain",
            extracted_text_context=summary,
            file_size=file_size,
            created_at=datetime.datetime.utcnow()
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return FileUploadResponse(
            id=db_file.id,
            conversation_id=db_file.conversation_id,
            filename=db_file.filename,
            file_type=db_file.file_type,
            file_size=db_file.file_size,
            extracted_text_summary=summary,
            created_at=db_file.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
