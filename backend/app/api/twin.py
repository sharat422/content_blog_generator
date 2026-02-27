
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.security import verify_supabase_token
from app.services.permissions import require_pro_for_twin
from app.services.supabase_service import (
    fetch_user_profile,
    save_user_profile,
    load_memories,
    save_memory,
    get_user_plan
)
from app.synthetic_engine.synth_core import SynthCore, TwinProfile
from app.services.llm_service import llm_client


router = APIRouter()


@router.get("/test-echo")
def test_echo():
    return {"message": "ALIVE_AND_CURRENT_CODE_V1"}


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

# Local is_pro_user removed in favor of permissions.require_pro_for_twin


# ============================
# GET PROFILE
# ============================

@router.get("/profile")
async def get_twin_profile(user=Depends(verify_supabase_token)):
    try:
        user_id = user["id"]

        profile = fetch_user_profile(user_id)

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

        resp = {
            "profile": profile,
            "memories": memories,
            "is_pro": await require_pro_for_twin(user)
        }
        print(f"[DEBUG TWIN] Profile resp for {user_id}: is_pro={resp['is_pro']}")
        return resp
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": traceback.format_exc()})


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
    print(f"DEBUG: Generating twin output for user {user_id}")

    try:
        # 🔒 PRO CHECK (Trial included)
        allowed = await require_pro_for_twin(user)
        if not allowed:
            print(f"DEBUG: User {user_id} is not PRO or in Trial")
            raise HTTPException(status_code=403, detail="Twin is available only for PRO or Trial users.")

        # Load profile
        profile_data = fetch_user_profile(user_id)
        if not profile_data:
            print(f"DEBUG: Profile not found for user {user_id}. Using defaults.")
            profile_data = {
                "user_id": user_id,
                "bio": "Your AI Twin",
                "tone": "Friendly",
                "creativity": 0.7
            }

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
            "response": response_text, # Add for compatibility
            "is_pro": True,
            "memory_used": True,
            "remaining_credits": 999  # optional
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in /api/twin/generate: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
