from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationUpdateRequest,
    ConversationResponse,
    MessageCreateRequest,
    MessageResponse,
)
from app.services.conversations import (
    create_conversation,
    list_conversations,
    get_conversation,
    update_conversation,
    delete_conversation,
    get_conversation_messages,
    send_message,
)

router = APIRouter()

from typing import List, Optional

@router.get("", response_model=List[ConversationResponse])
def get_all_conversations(
    q: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return list_conversations(db, current_user.id, search_query=q)

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def new_conversation(
    req: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_conversation(db, current_user.id, req)

from app.schemas.context import ContextPassportResponse
from app.services.memory import build_context_passport

@router.get("/{id}", response_model=ConversationResponse)
def get_single_conversation(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = get_conversation(db, current_user.id, id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conv

@router.get("/{id}/passport", response_model=ContextPassportResponse)
def get_passport(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = get_conversation(db, current_user.id, id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return build_context_passport(db, id)

@router.patch("/{id}", response_model=ConversationResponse)
def update_existing_conversation(
    id: str,
    req: ConversationUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = update_conversation(db, current_user.id, id, req)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conv

@router.delete("/{id}")
def remove_conversation(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = delete_conversation(db, current_user.id, id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}

@router.get("/{id}/messages", response_model=List[MessageResponse])
def get_messages(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_conversation_messages(db, current_user.id, id)

@router.post("/{id}/messages", response_model=MessageResponse)
def post_message(
    id: str,
    req: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return send_message(db, current_user.id, id, req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
