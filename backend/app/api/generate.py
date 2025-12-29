from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.llm_service import generate_content
from app.config.plan_limits import get_limits
from app.services.security import verify_supabase_token
from app.services.supabase_service import get_user_usage, increment_usage, get_user_profile, get_user_credits, deduct_credits
from app.config.credit_costs import get_cost
from pydantic import BaseModel
from uuid import UUID

router = APIRouter()

class GenerateSchema(BaseModel):
    prompt: str
    type: str = "text"  # text, image, audio
    action: str = "generate"  # optional: used for credit costs

def check_and_deduct(user_id: str, action: str):
    credits = get_user_credits(user_id)

    cost = get_cost(action)

    if credits is None:
        raise HTTPException(500, "Credits not initialized.")
    
    if credits["credits"] < cost:
        raise HTTPException(402, "Not enough credits. Please upgrade.")

    deduct_credits(user_id, cost)
    return True    

@router.post("/")
def generate(body: GenerateSchema,
    user=Depends(verify_supabase_token), db: Session = Depends(get_db)):
    user_id = user["id"]
    # -------------------------
    # PLAN LIMIT CHECK
    # -------------------------
    profile = get_user_profile(user_id)
    plan = profile.get("plan", "free")

    limits = get_limits(plan)
    max_free = limits["max_free_generations"]
    usage = get_user_usage(user_id)

    if usage >= max_free:
        raise HTTPException(
            status_code=403,
            detail="You have reached your free limit. Upgrade to PRO for unlimited generations."
        )

    # Count usage BEFORE running LLM
    increment_usage(user_id)

    # -------------------------
    # RUN LLM
    # -------------------------
    try:
        evolve_personality()
        #SYNC CALL - correct for llm.py
        result = generate_content(
        db=db, 
        user_id = user_id, 
        prompt = body.prompt,
        output_type = body.type,)
        return {"content": result, "remaining_free": max_free - (usage + 1 )}
        
    except Exception as e:
        raise HTTPException(status_code = 500, detail=str(e))
