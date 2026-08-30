from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.memory import MemoryCreateRequest, MemoryUpdateRequest, MemoryResponse
from app.services.memory import (
    create_memory,
    get_conversation_memories,
    update_memory,
    delete_memory,
)

router = APIRouter()

@router.get("/conversations/{id}/memory", response_model=List[MemoryResponse])
def get_memories(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_conversation_memories(db, id)

@router.post("/conversations/{id}/memory", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def add_memory(
    id: str,
    req: MemoryCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_memory(db, id, req)

@router.patch("/memory/{id}", response_model=MemoryResponse)
def patch_memory(
    id: str,
    req: MemoryUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mem = update_memory(db, id, req)
    if not mem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory item not found")
    return mem

@router.delete("/memory/{id}")
def remove_memory(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = delete_memory(db, id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory item not found")
    return {"message": "Memory item deleted successfully"}
