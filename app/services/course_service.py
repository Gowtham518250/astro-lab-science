from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models import Course, Lesson, Enrollment, Favorite

def get_courses(
    db: Session,
    category: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    page: int = 1,
    limit: int = 10,
    user_id: Optional[str] = None,
) -> dict:
    query = db.query(Course).filter(Course.isPublished == True)

    if category and category != "All":
        query = query.filter(Course.category.ilike(category))
    if level:
        query = query.filter(Course.level == level)
    if featured is not None:
        query = query.filter(Course.isFeatured == featured)
    if search:
        query = query.filter(
            or_(
                Course.title.ilike(f"%{search}%"),
                Course.description.ilike(f"%{search}%"),
                Course.instructor.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    offset = (page - 1) * limit
    courses = query.offset(offset).limit(limit).all()
    pages = max(1, (total + limit - 1) // limit)

    # Build enrolled and favorited sets for current user
    enrolled_ids: set = set()
    favorited_ids: set = set()
    if user_id:
        enrolled = db.query(Enrollment.courseId).filter(Enrollment.userId == user_id).all()
        enrolled_ids = {r[0] for r in enrolled}
        faved = db.query(Favorite.courseId).filter(Favorite.userId == user_id).all()
        favorited_ids = {r[0] for r in faved}

    result = []
    for c in courses:
        lessons_count = db.query(Lesson).filter(Lesson.courseId == c.id).count()
        enrollments_count = db.query(Enrollment).filter(Enrollment.courseId == c.id).count()
        result.append(serialize_course(c, lessons_count, enrollments_count,
                                       c.id in enrolled_ids, c.id in favorited_ids))

    return {"courses": result, "total": total, "pages": pages}


def get_course_by_id(db: Session, course_id: str, user_id: Optional[str] = None) -> Optional[dict]:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return None

    lessons = db.query(Lesson).filter(Lesson.courseId == course_id).order_by(Lesson.position).all()
    is_enrolled = False
    is_favorited = False
    if user_id:
        is_enrolled = db.query(Enrollment).filter(
            Enrollment.userId == user_id, Enrollment.courseId == course_id
        ).first() is not None
        is_favorited = db.query(Favorite).filter(
            Favorite.userId == user_id, Favorite.courseId == course_id
        ).first() is not None

    enrollments_count = db.query(Enrollment).filter(Enrollment.courseId == course_id).count()
    data = serialize_course(course, len(lessons), enrollments_count, is_enrolled, is_favorited)
    data["lessons"] = [serialize_lesson(l) for l in lessons]
    return data


def serialize_course(course: Course, lessons_count: int, enrollments_count: int,
                     is_enrolled: bool = False, is_favorited: bool = False) -> dict:
    return {
        "id": course.id,
        "title": course.title,
        "slug": course.slug,
        "description": course.description,
        "thumbnail": course.thumbnail,
        "category": course.category,
        "instructor": course.instructor,
        "level": course.level,
        "duration": course.duration,
        "price": course.price,
        "discount": course.discount,
        "isPublished": course.isPublished,
        "isPremium": course.isPremium,
        "isFeatured": course.isFeatured,
        "createdAt": course.createdAt,
        "updatedAt": course.updatedAt,
        "isEnrolled": is_enrolled,
        "isFavorited": is_favorited,
        "_count": {"lessons": lessons_count, "enrollments": enrollments_count},
    }


def serialize_lesson(lesson: Lesson) -> dict:
    return {
        "id": lesson.id,
        "title": lesson.title,
        "description": lesson.description,
        "videoUrl": lesson.videoUrl,
        "duration": lesson.duration,
        "position": lesson.position,
        "isFree": lesson.isFree,
        "courseId": lesson.courseId,
    }
