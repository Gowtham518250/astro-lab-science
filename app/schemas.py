from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Common config to allow reading ORM models directly
class BaseORMModel(BaseModel):
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseORMModel):
    name: str
    email: EmailStr
    image: Optional[str] = None
    role: str = "STUDENT"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    action: str  # login, register, logout
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    name: Optional[str] = None # For register action
    role: Optional[str] = None # For customer vs user

class LoginPayload(BaseModel):
    email: EmailStr
    password: str

class RegisterPayload(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "USER"

class AuthUserResponse(UserBase):
    id: str
    streak: int
    totalXP: int
    createdAt: datetime
    updatedAt: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse

# Lesson schemas
class LessonBase(BaseORMModel):
    id: str
    title: str
    description: str
    videoUrl: str
    duration: int
    position: int
    isFree: bool
    courseId: str

class CourseBase(BaseORMModel):
    id: str
    title: str
    slug: str
    description: str
    thumbnail: str
    category: str
    instructor: str
    level: str
    duration: int
    price: float
    discount: float
    isPublished: bool
    isPremium: bool
    isFeatured: bool
    createdAt: datetime
    updatedAt: datetime

class CourseCount(BaseModel):
    lessons: int
    enrollments: int

class CourseDetailResponse(CourseBase):
    lessons: List[LessonBase] = []
    isEnrolled: Optional[bool] = False
    _count: Optional[CourseCount] = None

class CourseListResponse(BaseORMModel):
    courses: List[CourseDetailResponse]
    total: int
    pages: int

# Progress schemas
class ProgressUpdate(BaseModel):
    lessonId: str
    courseId: str
    completed: bool
    watchedSecs: int

class CourseEnrolledDetail(BaseORMModel):
    id: str
    title: str
    slug: str
    thumbnail: str
    level: str
    duration: int

class EnrollmentResponse(BaseORMModel):
    id: str
    userId: str
    courseId: str
    progress: float
    completed: bool
    enrolledAt: datetime
    completedAt: Optional[datetime] = None
    course: CourseEnrolledDetail

class CertificateResponse(BaseORMModel):
    id: str
    userId: str
    courseName: str
    courseId: Optional[str] = None
    grade: str
    issuedAt: datetime
    course: Optional[CourseEnrolledDetail] = None

class NotificationResponse(BaseORMModel):
    id: str
    userId: str
    title: str
    message: str
    type: str
    isRead: bool
    createdAt: datetime
