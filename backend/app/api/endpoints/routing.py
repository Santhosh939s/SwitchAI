from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.routing import RoutingPreviewRequest, RoutingPreviewResponse
from app.services.routing import route_request

router = APIRouter()

@router.post("/preview", response_model=RoutingPreviewResponse)
def preview_route(
    req: RoutingPreviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return route_request(db, current_user.id, req.message, req.priority)
