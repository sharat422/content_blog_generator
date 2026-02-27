# app/api/auth.py

from fastapi import APIRouter, Depends
from app.services.security import get_current_user
from app.services.supabase_service import initialize_user_credits, get_user_credits

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {"user_id": user["id"]}


@router.post("/initialize")
def initialize(user=Depends(get_current_user)):
    """
    This runs on first login.
    If the user has no credits yet, give them initial 100 credits.
    """
    user_id = user["id"]

    existing = get_user_credits(user_id)
    if existing:
        return {"message": "Already initialized", "credits": existing["credits"]}

    # Give the first free 100 credits
    initialize_user_credits(user_id)

    return {"message": "Credits initialized", "credits": 100}

