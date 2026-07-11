from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Certificate, Course
from .auth import get_current_user_from_cookie

router = APIRouter(prefix="/certificates", tags=["certificates"])

@router.get("")
def get_user_certificates(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    certs = db.query(Certificate).filter(Certificate.userId == user.id).all()
    
    result = []
    for cert in certs:
        # Find course details to return course properties
        course = db.query(Course).filter(Course.id == cert.courseId).first()
        course_data = {
            "title": cert.courseName,
            "instructor": "Astro Lab Team",
            "thumbnail": "https://images.unsplash.com/photo-1579546929518-9e396f3cc809?auto=format&fit=crop&w=900&q=80"
        }
        if course:
            course_data["instructor"] = course.instructor
            course_data["thumbnail"] = course.thumbnail
            
        result.append({
            "id": cert.id,
            "userId": cert.userId,
            "courseName": cert.courseName,
            "courseId": cert.courseId,
            "grade": cert.grade,
            "issuedAt": cert.issuedAt,
            "course": course_data
        })
        
    return {"certificates": result}
