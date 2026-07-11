from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db
from ..models import Notification, User
from .auth import get_current_user_from_cookie

router = APIRouter(prefix="/notifications", tags=["notifications"])

class NotificationActionPayload(BaseModel):
    action: str
    id: Optional[str] = None
    userId: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None
    type: Optional[str] = "info"

@router.get("")
def get_notifications(
    request: Request,
    unread: bool = Query(False),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    query = db.query(Notification).filter(Notification.userId == user.id)
    if unread:
        query = query.filter(Notification.isRead == False)
        
    notifications = query.order_by(Notification.createdAt.desc()).limit(20).all()
    unread_count = db.query(Notification).filter(
        Notification.userId == user.id,
        Notification.isRead == False
    ).count()
    
    return {
        "notifications": [
            {
                "id": n.id,
                "userId": n.userId,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "isRead": n.isRead,
                "createdAt": n.createdAt
            }
            for n in notifications
        ],
        "unreadCount": unread_count
    }

@router.post("")
def handle_notification_action(
    payload: NotificationActionPayload,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    if payload.action == "markAllRead":
        db.query(Notification).filter(Notification.userId == user.id).update({"isRead": True})
        db.commit()
        return {"ok": True}
        
    elif payload.action == "markRead":
        if not payload.id:
            raise HTTPException(status_code=400, detail="Notification ID required")
        notification = db.query(Notification).filter(
            Notification.id == payload.id,
            Notification.userId == user.id
        ).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        notification.isRead = True
        db.commit()
        return {"ok": True}
        
    elif payload.action == "create":
        if user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Forbidden")
        if not payload.userId or not payload.title or not payload.message:
            raise HTTPException(status_code=400, detail="Missing required notification fields")
            
        notification = Notification(
            userId=payload.userId,
            title=payload.title,
            message=payload.message,
            type=payload.type or "info"
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return {
            "id": notification.id,
            "userId": notification.userId,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "isRead": notification.isRead,
            "createdAt": notification.createdAt
        }
        
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
