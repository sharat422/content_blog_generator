from fastapi import APIRouter, Depends
from app.services.security import verify_supabase_token
from app.services.supabase_service import get_user_credits

router = APIRouter(prefix="/api/credits", tags=["Credits"])

@router.get("/me")
def credits_me(user=Depends(verify_supabase_token)):
    user_id = user["id"]
    row = get_user_credits(user_id)

    if not row:
        return {"credits": 0}

    return {"credits": row["credits"]}
