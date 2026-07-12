from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database import get_db
from ..models import User, Server, Channel, Message
from ..security import get_current_user

router = APIRouter(tags=["Community"])

@router.get("/community/servers", response_model=Dict[str, Any])
def get_community_servers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    servers = db.query(Server).all()
    
    server_data = []
    for s in servers:
        channels = db.query(Channel).filter(Channel.serverId == s.id).all()
        server_data.append({
            "id": s.id,
            "name": s.name,
            "image": s.image,
            "isGlobal": s.isGlobal,
            "channels": [
                {
                    "id": c.id,
                    "name": c.name,
                    "type": c.type
                } for c in channels
            ]
        })
        
    return {
        "servers": server_data
    }

@router.get("/community/channels/{channel_id}/messages", response_model=Dict[str, Any])
def get_channel_messages(channel_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    messages = db.query(Message).filter(Message.channelId == channel_id).order_by(Message.createdAt.asc()).limit(50).all()
    
    msg_data = []
    for m in messages:
        user = db.query(User).filter(User.id == m.userId).first()
        msg_data.append({
            "id": m.id,
            "text": m.text,
            "createdAt": m.createdAt.isoformat() if m.createdAt else None,
            "user": {
                "id": user.id if user else "unknown",
                "name": user.name if user else "Unknown User",
                "avatar": user.image if user else "https://api.dicebear.com/7.x/avataaars/svg?seed=guest"
            }
        })
        
    return {
        "messages": msg_data
    }
