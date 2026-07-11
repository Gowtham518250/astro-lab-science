# backend/app/services/auth_service.py
from typing import Optional
from sqlalchemy.orm import Session
from ..models import User
from ..security import verify_password, get_password_hash, create_access_token
from ..config import settings
from datetime import timedelta

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashedPassword):
        return None
    return user

def create_user(db: Session, name: str, email: str, password: str, role: str = "STUDENT") -> User:
    hashed_password = get_password_hash(password)
    user = User(
        name=name,
        email=email,
        hashedPassword=hashed_password,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def build_token(user: User) -> str:
    return create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "totalXP": user.totalXP,
        "streak": user.streak,
        "image": user.image,
        "createdAt": user.createdAt,
        "updatedAt": user.updatedAt,
    }
