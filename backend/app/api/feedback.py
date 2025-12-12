from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Feedback
from app.services.personalization import update_user_preferences
from pydantic import BaseModel
from uuid import UUID

router = APIRouter()

class FeedbackSchema(BaseModel):
    user_id: UUID
    content_id: UUID
    score: int
    feedback_type: str
    notes: str = None

@router.post("/")
async def save_feedback(feedback: FeedbackSchema, db: Session = Depends(get_db)):
    db_feedback = Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    update_user_preferences(db, feedback.user_id, feedback)
    return {"message": "Feedback saved"}
