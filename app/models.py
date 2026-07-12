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
    hashedPassword = Column(String, nullable=False)
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
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="user", cascade="all, delete-orphan")
    support_tickets = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    organizations = relationship("Organization", back_populates="owner", cascade="all, delete-orphan")


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
    duration = Column(Integer, nullable=False)
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
    reviews = relationship("Review", back_populates="course", cascade="all, delete-orphan")
    course_modules = relationship("CourseModule", back_populates="course", cascade="all, delete-orphan")
    course_sections = relationship("CourseSection", back_populates="course", cascade="all, delete-orphan")
    course_documents = relationship("CourseDocument", back_populates="course", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")
    coding_assignments = relationship("CodingAssignment", back_populates="course", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="course", cascade="all, delete-orphan")
    forum_threads = relationship("ForumThread", back_populates="course", cascade="all, delete-orphan")
    live_classes = relationship("LiveClass", back_populates="course", cascade="all, delete-orphan")
    schedules = relationship("ScheduleItem", back_populates="course", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "Category"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    image = Column(String, nullable=True)

    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class Instructor(Base):
    __tablename__ = "Instructor"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    image = Column(String, nullable=True)
    website = Column(String, nullable=True)
    featured = Column(Boolean, default=False)

    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class Review(Base):
    __tablename__ = "Review"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    comment = Column(String, nullable=False)

    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="reviews")
    course = relationship("Course", back_populates="reviews")


class Coupon(Base):
    __tablename__ = "Coupon"

    id = Column(String, primary_key=True, default=generate_uuid)
    code = Column(String, unique=True, nullable=False, index=True)
    discountPercent = Column(Float, nullable=False)
    active = Column(Boolean, default=True)
    expiresAt = Column(DateTime, nullable=True)
    usageLimit = Column(Integer, nullable=True)
    usedCount = Column(Integer, default=0)
    minOrderAmount = Column(Float, default=0.0)

    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class PaymentProvider(Base):
    __tablename__ = "PaymentProvider"

    id = Column(String, primary_key=True, default=generate_uuid)
    ownerName = Column(String, nullable=False)
    razorpayKeyId = Column(String, nullable=True)
    razorpayKeySecret = Column(String, nullable=True)
    razorpayAccountId = Column(String, nullable=True)
    upiId = Column(String, nullable=True)
    qrCodeUrl = Column(String, nullable=True)
    terms = Column(String, nullable=True)
    isActive = Column(Boolean, default=True)

    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class Announcement(Base):
    __tablename__ = "Announcement"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    type = Column(String, default="info")
    isPublished = Column(Boolean, default=True)
    startsAt = Column(DateTime, nullable=True)
    endsAt = Column(DateTime, nullable=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class WishlistItem(Base):
    __tablename__ = "WishlistItem"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    createdAt = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="wishlist_items")
    course = relationship("Course")


class SupportTicket(Base):
    __tablename__ = "SupportTicket"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)
    category = Column(String, default="general")
    status = Column(String, default="open")
    priority = Column(String, default="medium")
    response = Column(String, nullable=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    resolvedAt = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="support_tickets")


class PlatformSetting(Base):
    __tablename__ = "PlatformSetting"

    id = Column(String, primary_key=True, default=generate_uuid)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class HelpArticle(Base):
    __tablename__ = "HelpArticle"

    id = Column(String, primary_key=True, default=generate_uuid)
    slug = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    category = Column(String, default="general")
    isPublished = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class ActivityLog(Base):
    __tablename__ = "ActivityLog"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=True)
    action = Column(String, nullable=False)
    entityType = Column(String, nullable=True)
    entityId = Column(String, nullable=True)
    log_metadata = Column(JSON, nullable=True)  # Renamed from metadata (reserved)
    createdAt = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="activity_logs")


class Organization(Base):
    __tablename__ = "Organization"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    website = Column(String, nullable=True)
    type = Column(String, default="company")
    ownerId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=True)
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="organizations")


class University(Base):
    __tablename__ = "University"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    country = Column(String, nullable=True)
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    departments = relationship("Department", back_populates="university", cascade="all, delete-orphan")


class Department(Base):
    __tablename__ = "Department"

    id = Column(String, primary_key=True, default=generate_uuid)
    universityId = Column(String, ForeignKey("University.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    university = relationship("University", back_populates="departments")


class CourseModule(Base):
    __tablename__ = "CourseModule"

    id = Column(String, primary_key=True, default=generate_uuid)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    position = Column(Integer, default=1)
    isPublished = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="course_modules")
    sections = relationship("CourseSection", back_populates="module", cascade="all, delete-orphan")


class CourseSection(Base):
    __tablename__ = "CourseSection"

    id = Column(String, primary_key=True, default=generate_uuid)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    moduleId = Column(String, ForeignKey("CourseModule.id", ondelete="CASCADE"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    position = Column(Integer, default=1)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="course_sections")
    module = relationship("CourseModule", back_populates="sections")


class CourseVideo(Base):
    __tablename__ = "CourseVideo"

    id = Column(String, primary_key=True, default=generate_uuid)
    lessonId = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    duration = Column(Integer, default=0)
    isPublished = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class CourseDocument(Base):
    __tablename__ = "CourseDocument"

    id = Column(String, primary_key=True, default=generate_uuid)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    fileType = Column(String, nullable=True)
    isPublished = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="course_documents")


class Assignment(Base):
    __tablename__ = "Assignment"

    id = Column(String, primary_key=True, default=generate_uuid)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    dueDate = Column(DateTime, nullable=True)
    maxScore = Column(Integer, default=100)
    isPublished = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="assignments")


class CodingAssignment(Base):
    __tablename__ = "CodingAssignment"

    id = Column(String, primary_key=True, default=generate_uuid)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    difficulty = Column(String, default="easy")
    starterCode = Column(String, nullable=True)
    isPublished = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="coding_assignments")


class PeerReview(Base):
    __tablename__ = "PeerReview"

    id = Column(String, primary_key=True, default=generate_uuid)
    assignmentId = Column(String, nullable=False)
    reviewerId = Column(String, nullable=False)
    submissionId = Column(String, nullable=False)
    rating = Column(Integer, default=5)
    comment = Column(String, nullable=True)
    createdAt = Column(DateTime, default=func.now())


class Quiz(Base):
    __tablename__ = "Quiz"

    id = Column(String, primary_key=True, default=generate_uuid)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    duration = Column(Integer, default=30)
    passingScore = Column(Integer, default=70)
    isPublished = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "QuizQuestion"

    id = Column(String, primary_key=True, default=generate_uuid)
    quizId = Column(String, ForeignKey("Quiz.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)
    options = Column(JSON, nullable=False)
    answer = Column(Integer, nullable=False)

    quiz = relationship("Quiz", back_populates="questions")


class Exam(Base):
    __tablename__ = "Exam"

    id = Column(String, primary_key=True, default=generate_uuid)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    duration = Column(Integer, default=60)
    passingScore = Column(Integer, default=70)
    isPublished = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="exams")


class ForumThread(Base):
    __tablename__ = "ForumThread"

    id = Column(String, primary_key=True, default=generate_uuid)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    isPinned = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="forum_threads")


class ForumPost(Base):
    __tablename__ = "ForumPost"

    id = Column(String, primary_key=True, default=generate_uuid)
    threadId = Column(String, ForeignKey("ForumThread.id", ondelete="CASCADE"), nullable=False)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    createdAt = Column(DateTime, default=func.now())


class LiveClass(Base):
    __tablename__ = "LiveClass"

    id = Column(String, primary_key=True, default=generate_uuid)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    startAt = Column(DateTime, nullable=False)
    durationMinutes = Column(Integer, default=60)
    meetingUrl = Column(String, nullable=True)
    isLive = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="live_classes")


class ScheduleItem(Base):
    __tablename__ = "ScheduleItem"

    id = Column(String, primary_key=True, default=generate_uuid)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    startAt = Column(DateTime, nullable=False)
    endAt = Column(DateTime, nullable=False)
    type = Column(String, default="lesson")
    createdAt = Column(DateTime, default=func.now())

    course = relationship("Course", back_populates="schedules")


class CalendarEvent(Base):
    __tablename__ = "CalendarEvent"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    startAt = Column(DateTime, nullable=False)
    endAt = Column(DateTime, nullable=False)
    description = Column(String, nullable=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class Message(Base):
    __tablename__ = "Message"

    id = Column(String, primary_key=True, default=generate_uuid)
    senderId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    receiverId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    conversationId = Column(String, nullable=False)
    content = Column(String, nullable=False)
    isRead = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=func.now())


class Subscription(Base):
    __tablename__ = "Subscription"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    planName = Column(String, nullable=False)
    status = Column(String, default="active")
    startAt = Column(DateTime, default=func.now())
    endAt = Column(DateTime, nullable=True)
    amount = Column(Float, default=0.0)
    createdAt = Column(DateTime, default=func.now())


class Scholarship(Base):
    __tablename__ = "Scholarship"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    courseId = Column(String, ForeignKey("Course.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, default=0.0)
    status = Column(String, default="pending")
    reason = Column(String, nullable=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class RefundRequest(Base):
    __tablename__ = "RefundRequest"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    paymentId = Column(String, nullable=False)
    amount = Column(Float, default=0.0)
    status = Column(String, default="pending")
    reason = Column(String, nullable=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class Invoice(Base):
    __tablename__ = "Invoice"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="pending")
    dueDate = Column(DateTime, nullable=True)
    paidAt = Column(DateTime, nullable=True)
    createdAt = Column(DateTime, default=func.now())


class ReportItem(Base):
    __tablename__ = "ReportItem"

    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="open")
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class ModerationItem(Base):
    __tablename__ = "ModerationItem"

    id = Column(String, primary_key=True, default=generate_uuid)
    entityType = Column(String, nullable=False)
    entityId = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default="pending")
    createdBy = Column(String, nullable=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class LocalizationSetting(Base):
    __tablename__ = "LocalizationSetting"

    id = Column(String, primary_key=True, default=generate_uuid)
    locale = Column(String, nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())


class Lesson(Base):
    __tablename__ = "Lesson"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    videoUrl = Column(String, nullable=False)
    duration = Column(Integer, default=0)
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
