from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Enrollment, LessonProgress, Lesson, Course, User, Certificate
from ..schemas import ProgressUpdate
from .auth import get_current_user_from_cookie

router = APIRouter(prefix="/progress", tags=["progress"])

@router.get("")
def get_user_progress(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    enrollments = db.query(Enrollment).filter(Enrollment.userId == user.id).all()
    
    result = []
    for enroll in enrollments:
        course = db.query(Course).filter(Course.id == enroll.courseId).first()
        if not course:
            continue
            
        lessons_count = db.query(Lesson).filter(Lesson.courseId == course.id).count()
        
        result.append({
            "id": enroll.id,
            "userId": enroll.userId,
            "courseId": enroll.courseId,
            "progress": enroll.progress,
            "completed": enroll.completed,
            "enrolledAt": enroll.enrolledAt,
            "completedAt": enroll.completedAt,
            "course": {
                "id": course.id,
                "title": course.title,
                "slug": course.slug,
                "thumbnail": course.thumbnail,
                "level": course.level,
                "duration": course.duration,
                "_count": {
                    "lessons": lessons_count
                }
            }
        })
        
    return {"enrollments": result}

@router.post("")
def update_progress(payload: ProgressUpdate, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    # Check if lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == payload.lessonId).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
        
    # Check enrollment
    enrollment = db.query(Enrollment).filter(
        Enrollment.userId == user.id,
        Enrollment.courseId == payload.courseId
    ).first()
    if not enrollment:
        raise HTTPException(status_code=400, detail="User is not enrolled in this course")
        
    # Find or create LessonProgress
    progress = db.query(LessonProgress).filter(
        LessonProgress.userId == user.id,
        LessonProgress.lessonId == payload.lessonId
    ).first()
    
    just_completed = False
    
    if not progress:
        progress = LessonProgress(
            userId=user.id,
            lessonId=payload.lessonId,
            completed=payload.completed,
            watchedSecs=payload.watchedSecs
        )
        db.add(progress)
        if payload.completed:
            just_completed = True
    else:
        if not progress.completed and payload.completed:
            just_completed = True
        progress.completed = payload.completed
        progress.watchedSecs = max(progress.watchedSecs, payload.watchedSecs)
        
    db.commit()
    
    # Award XP for lesson completion
    if just_completed:
        user.totalXP += 50
        user.streak = max(user.streak + 1, 1) # simple streak logic
        db.commit()
        
    # Calculate overall course progress
    total_lessons = db.query(Lesson).filter(Lesson.courseId == payload.courseId).count()
    if total_lessons > 0:
        # Find completed lessons count for this course
        completed_lessons = db.query(LessonProgress).join(Lesson).filter(
            LessonProgress.userId == user.id,
            Lesson.courseId == payload.courseId,
            LessonProgress.completed == True
        ).count()
        
        progress_percentage = (completed_lessons / total_lessons) * 100
        enrollment.progress = round(progress_percentage, 2)
        
        if progress_percentage >= 100.0 and not enrollment.completed:
            enrollment.completed = True
            enrollment.completedAt = datetime.now()
            user.totalXP += 200 # bonus XP for finishing course
            
            # Issue certificate
            cert_exists = db.query(Certificate).filter(
                Certificate.userId == user.id,
                Certificate.courseId == payload.courseId
            ).first()
            if not cert_exists:
                new_cert = Certificate(
                    userId=user.id,
                    courseName=lesson.course.title,
                    courseId=payload.courseId,
                    grade="Pass"
                )
                db.add(new_cert)
                
        db.commit()
        
    return {"success": True, "progress": enrollment.progress, "completed": enrollment.completed}
