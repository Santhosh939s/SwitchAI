from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.usage import UsageDashboardResponse
from app.services.usage import get_usage_metrics

router = APIRouter()

@router.get("", response_model=UsageDashboardResponse)
def get_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_usage_metrics(db, current_user.id)
