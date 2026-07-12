from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..services import get_courses, get_course_by_id
from .auth import get_current_user
from ..cache import get_cache, set_cache

from pydantic import BaseModel
import re
import uuid

router = APIRouter(prefix="/courses", tags=["courses"])

class CourseCreate(BaseModel):
    title: str
    price: float = 0.0
    category: str = "Science"
    previewVideo: Optional[str] = None
    mainVideo: Optional[str] = None

@router.post("")
def create_course(payload: CourseCreate, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin only")
        
    slug = re.sub(r'[^a-z0-9]+', '-', payload.title.lower()).strip('-')
    
    # Check if slug exists
    from ..models import Course
    existing = db.query(Course).filter(Course.slug == slug).first()
    if existing:
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        
    course = Course(
        title=payload.title,
        slug=slug,
        description="A comprehensive new course on " + payload.title,
        thumbnail="https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=2048&auto=format&fit=crop",
        category=payload.category,
        instructor=user.name,
        price=payload.price,
        previewVideo=payload.previewVideo,
        mainVideo=payload.mainVideo,
        isPublished=True,
        duration=120
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    
    # Invalidate cache
    set_cache(f"courses:list:*", None, expire_seconds=0)
    
    return course


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
    user = get_current_user(request, db)
    
    # Cache Key based on query params and user context (users might have 'enrolled' flags in the list response)
    # If the list is identical for all users, we shouldn't include user_id. But since we do, we must cache per user or anonymous.
    user_id_str = user.id if user else "anonymous"
    cache_key = f"courses:list:cat={category}:lvl={level}:q={search}:feat={featured}:p={page}:l={limit}:u={user_id_str}"
    
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    result = get_courses(
        db,
        category=category,
        level=level,
        search=search,
        featured=featured,
        page=page,
        limit=limit,
        user_id=user.id if user else None,
    )
    
    # Cache for 15 minutes
    set_cache(cache_key, result, expire_seconds=900)
    return result


@router.get("/{course_id}")
def get_course(course_id: str, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    
    user_id_str = user.id if user else "anonymous"
    cache_key = f"course:{course_id}:u={user_id_str}"
    
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data
        
    course = get_course_by_id(db, course_id, user_id=user.id if user else None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Cache for 5 minutes
    set_cache(cache_key, course, expire_seconds=300)
    return course
