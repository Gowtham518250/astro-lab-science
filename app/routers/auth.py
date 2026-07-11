from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import User
from ..security import verify_access_token
from ..services import authenticate_user, create_user, build_token, serialize_user, get_user_by_email
from ..schemas import UserLogin
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        return None
    payload = verify_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        samesite="lax",
        path="/",
        max_age=settings.access_token_expire_minutes * 60,
    )


@router.get("")
def check_session(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return {"user": None}
    return {"user": serialize_user(user)}


@router.post("")
def auth_action(payload: UserLogin, response: Response, request: Request, db: Session = Depends(get_db)):
    if payload.action == "login":
        if not payload.email or not payload.password:
            raise HTTPException(status_code=400, detail="Email and password are required")

        user = authenticate_user(db, payload.email, payload.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = build_token(user)
        _set_auth_cookie(response, token)
        return {"user": serialize_user(user)}

    elif payload.action == "register":
        if not payload.email or not payload.password or not payload.name:
            raise HTTPException(status_code=400, detail="Name, email, and password are required")

        if get_user_by_email(db, payload.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        user = create_user(db, name=payload.name, email=payload.email, password=payload.password)
        token = build_token(user)
        _set_auth_cookie(response, token)
        return {"user": serialize_user(user)}

    elif payload.action == "logout":
        response.delete_cookie(key=settings.session_cookie_name, path="/")
        return {"success": True}

    else:
        raise HTTPException(status_code=400, detail="Invalid action")
