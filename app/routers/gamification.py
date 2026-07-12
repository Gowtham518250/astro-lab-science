from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database import get_db
from ..models import User, SkillTrack, SkillNode
from ..security import get_current_user

router = APIRouter(tags=["Gamification"])

@router.get("/gamification/me", response_model=Dict[str, Any])
def get_user_gamification(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Mock returning the tracks based on the DB schema
    tracks = db.query(SkillTrack).all()
    
    track_data = []
    for t in tracks:
        nodes = db.query(SkillNode).filter(SkillNode.trackId == t.id).all()
        track_data.append({
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "icon": t.icon,
            "color": t.color,
            "progress": 50, # Mock progress based on user stats
            "nodes": [
                {
                    "id": n.id,
                    "title": n.title,
                    "type": n.type,
                    "status": "completed" if n.type == "foundation" else "locked" # Mock
                } for n in nodes
            ]
        })
        
    return {
        "totalXP": current_user.totalXP,
        "globalRank": (current_user.totalXP // 1000) + 1,
        "tracks": track_data
    }
