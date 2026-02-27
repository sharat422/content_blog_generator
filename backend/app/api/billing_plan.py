from fastapi import APIRouter, Depends
from app.services.security import verify_supabase_token
from app.services.supabase_service import fetch_user_profile
from app.services.permissions import is_in_free_trial

router = APIRouter(prefix="/api/billing", tags=["Billing"])

@router.get("/my-plan")
def my_plan(user=Depends(verify_supabase_token)):
    profile = fetch_user_profile(user["id"])
    
    # Check for 7-day trial
    if is_in_free_trial(user):
        return {"plan": "pro", "trial": True}
        
    if not profile:
        return {"plan": "free"}
    return {"plan": profile.get("plan", "free")}
