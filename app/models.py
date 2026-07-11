import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"

class CourseLevel(str, enum.Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "User"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashedPassword = Column(String, nullable=False) # Changed from password to hashedPassword
    emailVerified = Column(Boolean, default=False)
    image = Column(String, nullable=True)
    role = Column(String, default="STUDENT")

    streak = Column(Integer, default=0)
    totalXP = Column(Integer, default=0)
    lastLoginAt = Column(DateTime, nullable=True)

    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("LessonProgress", back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "Course"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
    category = Column(String, default="Science")
    instructor = Column(String, default="Astro Lab Team")
    level = Column(String, default="BEGINNER")
    duration = Column(Integer, nullable=False) # in minutes
    price = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)

    isPublished = Column(Boolean, default=False)
    isPremium = Column(Boolean, default=False)
    isFeatured = Column(Boolean, default=False)

    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="course", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "Lesson"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    videoUrl = Column(String, nullable=False)
    duration = Column(Integer, default=0) # in seconds
    position = Column(Integer, nullable=False)
    isFree = Column(Boolean, default=False)

    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    course = relationship("Course", back_populates="lessons")
    progress = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "Enrollment"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)

    progress = Column(Float, default=0.0)
    completed = Column(Boolean, default=False)

    enrolledAt = Column(DateTime, default=func.now())
    completedAt = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class LessonProgress(Base):
    __tablename__ = "LessonProgress"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    lessonId = Column(String, ForeignKey("Lesson.id", ondelete="CASCADE"), nullable=False)

    completed = Column(Boolean, default=False)
    watchedSecs = Column(Integer, default=0)

    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")


class Payment(Base):
    __tablename__ = "Payment"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)

    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    method = Column(String, default="card")
    status = Column(String, default="PENDING")
    transactionId = Column(String, unique=True, nullable=True)
    couponCode = Column(String, nullable=True)
    discount = Column(Float, default=0.0)

    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="payments")
    course = relationship("Course", back_populates="payments")


class Favorite(Base):
    __tablename__ = "Favorite"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)

    createdAt = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="favorites")
    course = relationship("Course", back_populates="favorites")


class Certificate(Base):
    __tablename__ = "Certificate"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    courseName = Column(String, nullable=False)
    courseId = Column(String, nullable=True)
    grade = Column(String, default="Pass")

    issuedAt = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="certificates")


class Notification(Base):
    __tablename__ = "Notification"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, default="info")
    isRead = Column(Boolean, default=False)

    createdAt = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="notifications")


class Quiz(Base):
    __tablename__ = "Quiz"

    id = Column(String, primary_key=True, default=generate_uuid)
    courseId = Column(String, nullable=False)
    title = Column(String, nullable=False)

    createdAt = Column(DateTime, default=func.now())
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "QuizQuestion"

    id = Column(String, primary_key=True, default=generate_uuid)
    quizId = Column(String, ForeignKey("Quiz.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)
    options = Column(JSON, nullable=False) # JSON list of option strings
    answer = Column(Integer, nullable=False) # index of correct option

    quiz = relationship("Quiz", back_populates="questions")
