from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db
from ..models import Favorite, Course
from .auth import get_current_user_from_cookie

router = APIRouter(prefix="/favorites", tags=["favorites"])

class FavoriteRequest(BaseModel):
    courseId: str

@router.get("")
def get_favorites(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    favorites = db.query(Favorite).filter(Favorite.userId == user.id).all()

    result = []
    for fav in favorites:
        course = db.query(Course).filter(Course.id == fav.courseId).first()
        if not course:
            continue
        result.append({
            "id": fav.id,
            "courseId": fav.courseId,
            "createdAt": fav.createdAt,
            "course": {
                "id": course.id,
                "title": course.title,
                "slug": course.slug,
                "thumbnail": course.thumbnail,
                "category": course.category,
                "instructor": course.instructor,
                "level": course.level,
                "duration": course.duration,
                "price": course.price,
                "discount": course.discount,
                "isPremium": course.isPremium,
            }
        })

    return {"favorites": result}

@router.post("")
def toggle_favorite(payload: FavoriteRequest, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    existing = db.query(Favorite).filter(
        Favorite.userId == user.id,
        Favorite.courseId == payload.courseId
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"favorited": False}
    else:
        fav = Favorite(userId=user.id, courseId=payload.courseId)
        db.add(fav)
        db.commit()
        return {"favorited": True}
