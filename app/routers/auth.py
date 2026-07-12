from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import User
from ..security import verify_access_token
from ..services import authenticate_user, create_user, build_token, serialize_user, get_user_by_email
from ..schemas import UserLogin, LoginPayload, RegisterPayload
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    token = None
    # 1. Try to get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    # 2. Fallback to HttpOnly cookie
    if not token:
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


def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    return get_current_user(request, db)


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
    user = get_current_user(request, db)
    if not user:
        return {"user": None}
    return {"user": serialize_user(user)}


@router.post("/login", response_model=None)
def login_endpoint(payload: LoginPayload, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = build_token(user)
    _set_auth_cookie(response, token)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user)
    }


@router.post("/register", response_model=None)
def register_endpoint(payload: RegisterPayload, response: Response, db: Session = Depends(get_db)):
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Allows role to be specified (e.g. USER, CUSTOMER, STUDENT)
    user = create_user(db, name=payload.name, email=payload.email, password=payload.password, role=payload.role.upper() if payload.role else "USER")
    
    # Trigger background task
    try:
        import worker
        worker.send_welcome_email_task.delay(user.email, user.name)
    except Exception as e:
        print(f"Failed to queue welcome email: {e}")

    token = build_token(user)
    _set_auth_cookie(response, token)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user)
    }


@router.post("/logout")
def logout_endpoint(response: Response):
    response.delete_cookie(key=settings.session_cookie_name, path="/")
    return {"success": True}


@router.post("")
def auth_action_legacy(payload: UserLogin, response: Response, request: Request, db: Session = Depends(get_db)):
    # Legacy fallback endpoint
    if payload.action == "login":
        if not payload.email or not payload.password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        user = authenticate_user(db, payload.email, payload.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        token = build_token(user)
        _set_auth_cookie(response, token)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": serialize_user(user)
        }

    elif payload.action == "register":
        if not payload.email or not payload.password or not payload.name:
            raise HTTPException(status_code=400, detail="Name, email, and password are required")
        if get_user_by_email(db, payload.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        role_to_use = payload.role.upper() if getattr(payload, "role", None) else "STUDENT"
        user = create_user(db, name=payload.name, email=payload.email, password=payload.password, role=role_to_use)
        
        try:
            import worker
            worker.send_welcome_email_task.delay(user.email, user.name)
        except Exception as e:
            print(f"Failed to queue welcome email: {e}")

        token = build_token(user)
        _set_auth_cookie(response, token)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": serialize_user(user)
        }

    elif payload.action == "logout":
        response.delete_cookie(key=settings.session_cookie_name, path="/")
        return {"success": True}
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
