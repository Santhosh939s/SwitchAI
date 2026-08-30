import uuid
import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserUpdateRequest
from app.core.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower().strip()).first()

def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, req: UserRegisterRequest) -> User:
    user = User(
        id=str(uuid.uuid4()),
        email=req.email.lower().strip(),
        name=req.name or req.email.split('@')[0].capitalize(),
        password_hash=get_password_hash(req.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_profile(db: Session, user_id: str, req: UserUpdateRequest) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    if req.email and req.email.lower().strip() != user.email:
        existing = get_user_by_email(db, req.email)
        if existing and existing.id != user_id:
            raise ValueError("Email is already taken by another user")
        user.email = req.email.lower().strip()

    if req.name is not None:
        user.name = req.name.strip()

    user.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
