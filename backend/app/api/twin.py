# ==========================================
# PATCHED twin.py — FULL WORKING VERSION
# ==========================================

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.security import verify_supabase_token
from app.services.permissions import require_pro_for_twin
from app.services.supabase_service import (
    get_user_profile,
    save_user_profile,
    load_memories,
    save_memory,
)
from app.synthetic_engine.synth_core import SynthCore, TwinProfile
from app.services.llm_service import llm_client


router = APIRouter(prefix="/twin")   # << IMPORTANT — fixes 404 issues


# ============================
# REQUEST MODELS
# ============================

class TwinUpdateRequest(BaseModel):
    bio: str
    tone: str
    goals: str
    creativity: float = 0.7


class TwinGenerateRequest(BaseModel):
    prompt: str
    mode: str = "reflect"


# ============================
# GET PROFILE
# ============================

@router.get("/profile")
async def get_twin_profile(user=Depends(verify_supabase_token)):
    user_id = user["id"]

    profile = get_user_profile(user_id)

    if not profile:
        profile = {
            "user_id": user_id,
            "bio": "",
            "tone": "Friendly",
            "goals": "",
            "creativity": 0.7,
        }

    memories = load_memories(user_id)

    # UI expects user_id to exist
    profile["user_id"] = user_id

    return {
        "profile": profile,
        "memories": memories,
        "is_pro": await require_pro_for_twin(user_id)
    }


# ============================
# UPDATE PROFILE
# ============================

@router.post("/profile")
async def update_twin_profile(req: TwinUpdateRequest, user=Depends(verify_supabase_token)):
    user_id = user["id"]

    save_user_profile(
        user_id=user_id,
        bio=req.bio,
        tone=req.tone,
        goals=req.goals,
        creativity=req.creativity
    )

    return {"status": "success", "message": "Twin profile updated!"}


# ============================
# GENERATE TWIN RESPONSE
# ============================

@router.post("/generate")
async def generate_twin_output(req: TwinGenerateRequest, user=Depends(verify_supabase_token)):
    user_id = user["id"]

    # 🔒 PRO CHECK
    allowed = await require_pro_for_twin(user_id)
    if not allowed:
        return JSONResponse(
            status_code=403,
            content={
                "error": "Twin is available only for PRO users.",
                "is_pro": False,
                "output": ""
            }
        )

    # Load profile
    profile_data = get_user_profile(user_id)
    if not profile_data:
        raise HTTPException(status_code=400, detail="Twin profile not found.")

    memories = load_memories(user_id)

    profile = TwinProfile(
        user_id=user_id,
        display_name=profile_data.get("bio", "Your AI Twin"),
        tone=profile_data.get("tone", "Friendly"),
        creativity=profile_data.get("creativity", 0.7),
        favorite_topics=[],
        memories=memories
    )

    engine = SynthCore(llm_client, profile)

    # IMPORTANT: use proper Grok API
    response_text = await engine.generate(
        prompt=req.prompt,
        mode=req.mode
    )

    # Save memory
    save_memory(user_id, req.prompt, "user")
    save_memory(user_id, response_text, "twin")

    # UI compatible response
    return {
        "output": response_text,
        "is_pro": True,
        "memory_used": True,
        "remaining_credits": 999  # optional
    }
