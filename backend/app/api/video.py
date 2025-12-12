# app/api/video.py

from typing import List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.video_planner import generate_video_plan, SceneModel
from app.services.video_renderer import render_video_to_supabase
# 🌟 UPDATED: Ensure get_current_user is imported for authentication
from app.services.security import get_current_user 
from app.services.supabase_service import deduct_credits # <-- NEW
from app.config import get_cost # <-- NEW (Uses cost for "video_script" which is 8)

router = APIRouter(prefix="/api/video", tags=["Video"])


class PlanRequest(BaseModel):
    topic: str
    style: str = "informative"


class RenderRequest(BaseModel):
    scenes: List[SceneModel]
    with_voiceover: bool = False
    with_music: bool = True  # 🌟 NEW: Added with_music control


@router.post("/plan")
def plan_video(
    req: PlanRequest,
    user=Depends(get_current_user) # 🌟 NEW: Requires authentication for credit check
):
    """
    Step 1: Generate scenes from topic for Shorts/Reels.
    """
    # Note: Credit deduction for the plan happens inside generate_video_plan (or should soon)
    user_id = user["id"]  # Get user_id for credit deduction
    cost = get_cost("video_script")  # Get cost for video script generation
    try:
        # 👇 Deduct credits (will be bypassed by Admin logic in step 2)
        deduct_credits(user_id, cost) 
    except ValueError as e:
        # Not enough credits
        raise HTTPException(status_code=402, detail=str(e))
    try:
        scenes = generate_video_plan(req.topic, req.style)
        # Note: The 'scenes' returned here now includes the 'image_prompt' field.
        return {"scenes": [s.dict() for s in scenes]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan error: {e}")


@router.post("/render")
def render_video(
    req: RenderRequest,
    user=Depends(get_current_user) # 🌟 NEW: Requires authentication for credit deduction
):
    """
    Step 2: Render final video from scenes using the hybrid renderer.
    """
    user_id = user["id"] # Get user_id for credit deduction in renderer

    try:
        video_url = render_video_to_supabase(
            user_id=user_id, # 🌟 PASS user_id
            scenes=req.scenes,
            with_voiceover=req.with_voiceover,
            with_music=req.with_music, # 🌟 PASS with_music
        )
        return {"url": video_url}
    except Exception as e:
        # Catch explicit credit errors (402) or general errors (500)
        status_code = 402 if "credits" in str(e).lower() else 500
        raise HTTPException(status_code=status_code, detail=f"Render error: {e}")