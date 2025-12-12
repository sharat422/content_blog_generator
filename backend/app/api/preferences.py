from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import UserPreferences

router = APIRouter()

@router.get("/{user_id}")
def get_preferences(user_id: str, db: Session = Depends(get_db)):
    prefs = db.query(UserPreferences).filter_by(user_id=user_id).first()
    return prefs
