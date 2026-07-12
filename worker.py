import os
import time
from celery import Celery

# Redis URL from Railway environment variables
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery app
celery_app = Celery(
    "astrolab_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # In production, tasks that fail might be retried
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

@celery_app.task(name="send_welcome_email")
def send_welcome_email_task(user_email: str, user_name: str):
    """
    Simulates sending an email in the background without blocking the main API response.
    In a real app, you would integrate SendGrid, AWS SES, or Resend here.
    """
    print(f"[ASYNC TASK] Preparing to send welcome email to {user_name} ({user_email})...")
    time.sleep(2) # Simulate network delay
    print(f"[ASYNC TASK] Welcome email sent successfully to {user_email}!")
    return {"status": "sent", "email": user_email}

@celery_app.task(name="process_video_upload")
def process_video_upload_task(course_id: str, lesson_id: str, video_url: str):
    """
    Simulates a heavy Coursera-level video processing task (e.g. transcoding to HLS format for streaming).
    """
    print(f"[ASYNC TASK] Started processing video for lesson {lesson_id}...")
    time.sleep(5) # Simulate heavy CPU transcoding
    print(f"[ASYNC TASK] Video processing complete for {lesson_id}! HLS manifest generated.")
    return {"status": "processed", "lesson_id": lesson_id}

@celery_app.task(name="generate_certificate_pdf")
def generate_certificate_pdf_task(user_id: str, course_id: str):
    """
    Simulates generating a PDF certificate when a user completes a course.
    """
    print(f"[ASYNC TASK] Generating PDF certificate for user {user_id}, course {course_id}...")
    time.sleep(3) # Simulate PDF generation
    print(f"[ASYNC TASK] Certificate generated and emailed!")
    return {"status": "generated", "user_id": user_id, "course_id": course_id}
