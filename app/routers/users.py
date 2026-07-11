from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import User, Course, Enrollment, Payment
from .auth import get_current_user_from_cookie

router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
def list_users(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin only")

    users = db.query(User).order_by(User.createdAt.desc()).all()

    result = []
    for u in users:
        enrolled_count = db.query(Enrollment).filter(Enrollment.userId == u.id).count()
        result.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "totalXP": u.totalXP,
            "streak": u.streak,
            "image": u.image,
            "createdAt": u.createdAt,
            "_count": {"enrollments": enrolled_count}
        })

    return {"users": result, "total": len(result)}

@router.get("/me")
def get_me(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "totalXP": user.totalXP,
        "streak": user.streak,
        "image": user.image,
        "createdAt": user.createdAt,
        "updatedAt": user.updatedAt
    }

@router.get("/stats")
def get_stats(request: Request, db: Session = Depends(get_db)):
    """Admin-only: platform-wide stats for analytics dashboard"""
    user = get_current_user_from_cookie(request, db)
    if not user or user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin only")

    total_users = db.query(User).count()
    total_courses = db.query(Course).filter(Course.isPublished == True).count()
    total_enrollments = db.query(Enrollment).count()
    total_revenue = db.query(Payment).filter(Payment.status == "COMPLETED").all()
    revenue = sum(p.amount for p in total_revenue)
    completed_courses = db.query(Enrollment).filter(Enrollment.completed == True).count()

    return {
        "totalUsers": total_users,
        "totalCourses": total_courses,
        "totalEnrollments": total_enrollments,
        "totalRevenue": round(revenue, 2),
        "completedCourses": completed_courses,
    }
