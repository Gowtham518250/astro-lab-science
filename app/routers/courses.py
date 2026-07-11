from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..services import get_courses, get_course_by_id
from .auth import get_current_user_from_cookie

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("")
def list_courses(
    request: Request,
    category: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    featured: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    user = get_current_user_from_cookie(request, db)
    return get_courses(
        db,
        category=category,
        level=level,
        search=search,
        featured=featured,
        page=page,
        limit=limit,
        user_id=user.id if user else None,
    )


@router.get("/{course_id}")
def get_course(course_id: str, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    course = get_course_by_id(db, course_id, user_id=user.id if user else None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
