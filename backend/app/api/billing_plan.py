from fastapi import APIRouter, Depends
from app.services.security import verify_supabase_token
from app.services.supabase_service import get_user_profile

router = APIRouter(prefix="/api/billing", tags=["Billing"])

@router.get("/my-plan")
def my_plan(user=Depends(verify_supabase_token)):
    profile = get_user_profile(user["id"])
    return {"plan": profile.get("plan", "free")}
