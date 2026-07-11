from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Payment, Enrollment, Course, User
from .auth import get_current_user_from_cookie

router = APIRouter(prefix="/payment", tags=["payments"])

class PaymentRequest(BaseModel):
    courseId: str

@router.post("")
def process_payment(payload: PaymentRequest, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    course = db.query(Course).filter(Course.id == payload.courseId).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Check if already enrolled
    already_enrolled = db.query(Enrollment).filter(
        Enrollment.userId == user.id,
        Enrollment.courseId == payload.courseId
    ).first()
    
    if already_enrolled:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
        
    # Create Payment
    payment = Payment(
        userId=user.id,
        courseId=payload.courseId,
        amount=course.price,
        currency="INR",
        method="stripe_simulated",
        status="COMPLETED",
        transactionId=f"txn_{user.id[:4]}_{payload.courseId[:4]}_{int(db.query(Payment).count())}"
    )
    db.add(payment)
    
    # Create Enrollment
    enrollment = Enrollment(
        userId=user.id,
        courseId=payload.courseId,
        progress=0.0,
        completed=False
    )
    db.add(enrollment)
    
    # Award XP
    user.totalXP += 100
    db.commit()
    
    return {"success": True}
