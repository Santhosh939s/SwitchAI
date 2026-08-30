from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.provider import ProviderConnectRequest, ProviderStatusResponse, ProviderTestResponse
from app.services.providers import (
    list_provider_statuses,
    connect_provider,
    test_provider_connection,
    disconnect_provider,
)

router = APIRouter()

@router.get("", response_model=List[ProviderStatusResponse])
def get_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return list_provider_statuses(db, current_user.id)

@router.post("/{provider}/connect", response_model=ProviderStatusResponse)
def connect(
    provider: str,
    req: ProviderConnectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return connect_provider(
            db,
            user_id=current_user.id,
            provider=provider,
            api_key=req.api_key,
            default_model=req.default_model
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{provider}/test", response_model=ProviderTestResponse)
def test_connection(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return test_provider_connection(db, current_user.id, provider)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{provider}")
def disconnect(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = disconnect_provider(db, current_user.id, provider)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider}' was not connected"
        )
    return {"message": f"Successfully disconnected provider '{provider}'"}
