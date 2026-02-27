from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.config.plan_limits import get_limits
from app.services.security import verify_supabase_token
from app.synthetic_engine.synth_core import TwinCore, TwinProfile
from app.services.llm_service import llm_client
from app.services.supabase_service import get_usage, supabase, increment_usage, get_user_credits, deduct_credits
from app.config.credit_costs import get_cost
from pydantic import BaseModel



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
async def generate(body: GenerateSchema,
    user=Depends(verify_supabase_token), db: Session = Depends(get_db)):
    user_id = user["id"]

    # 1. Fetch user profile from Supabase
    profile_resp = supabase.table("twin_profiles").select("*").eq("user_id", user_id).maybe_single().execute()
    # Use existing profile or a default starting point
    profile_data = profile_resp.data if profile_resp.data else {
        "user_id": user_id,
        "tone": "Friendly",
        "creativity": 0.7,
        "favorite_topics": []
    }

    # 2. Check free limits
    usage = get_usage(user_id)
    used_count = usage.get("used_count", 0)
    if used_count >= 2: # Match FREE_LIMIT in permissions.py
        raise HTTPException(status_code=403, detail="limit_reached, get pro plan")

    # 3. Initialize the Twin Engine with the profile
    profile = TwinProfile(**profile_data)
    twin = TwinCore(llm=llm_client, profile=profile)
   
    # -------------------------
    # RUN LLM
    # -------------------------
    try:
        # 4. Generate content and evolve personality internally
        # This calls _score_importance and _evolve_personality automatically
        result = await twin.generate(
            prompt=f"Template: {body.type}. Prompt: {body.prompt}", 
            mode="create"
        )

        # 5. Save the evolved personality back to Supabase
        updated_profile = twin.profile.model_dump()
        supabase.table("twin_profiles").upsert(updated_profile).execute()

        # 6. Update usage count
        increment_usage(user_id)

        return {"content": result}

    except Exception as e:
        print(f"[ERROR] [GENERATE ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail="Generation failed")
