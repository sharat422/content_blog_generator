# app/routes/synth_twin.py
import httpx
import os
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.config import settings
from app.services.security import get_current_user, verify_supabase_token
from app.synthetic_engine.synth_core import TwinCore, SynthCore, TwinProfile
from app.services.supabase_service import (
    load_memories,
    save_memory,
)
from app.services.llm_service import client as llm_client  # <-- use main client

router = APIRouter(prefix="/api/twin", tags=["twin"])
core = TwinCore()

# --------------------------
# X.ai Grok-4 Client
# --------------------------
class XaiClient:
    def __init__(self):
        self.api_key = settings.MODEL_API_KEY
        self.base_url = os.getenv("MODEL_BASE_URL") or "https://api.x.ai/v1"

    async def chat(self, system_prompt: str, user_prompt: str, creativity: float):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": os.getenv("MODEL_NAME") or "grok-4",
            "temperature": creativity,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions", json=payload, headers=headers
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"X.ai error: {response.text}",
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]


llm_client = XaiClient()


# --------------------------
# Twin Models
# --------------------------

class TwinGenerateRequest(BaseModel):
    prompt: str
    mode: str = "reflect"  # reflect | plan | create


class TwinGenerateResponse(BaseModel):
    content: str
    mode: str
    timestamp: datetime


class TwinProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    tone: Optional[str] = None
    creativity: Optional[float] = None
    favorite_topics: Optional[List[str]] = None


class TwinProfileResponse(BaseModel):
    profile: TwinProfile

# ---------------------------
# Retry LLM Call Wrapper
# ---------------------------

async def safe_llm_generate(messages: list):
    """
    Production-grade retry handler for Grok API calls.
    Retries 3 times with increasing timeout.
    """

    timeouts = [15, 45, 90]  # escalating timeouts

    # Collapse messages[] into a single system + user prompt
    system_parts = []
    user_parts = []

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "system":
            system_parts.append(content)
        elif role == "user":
            user_parts.append(content)

    system_prompt = "\n\n".join(system_parts) or "You are a helpful assistant."
    user_prompt = "\n\n".join(user_parts)

    for attempt, timeout in enumerate(timeouts, start=1):
        try:
            print(f"🔄 Grok Request Attempt {attempt} (timeout={timeout}s)")

            # Our XaiClient.chat does the /chat/completions call internally
            content = await llm_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                creativity=0.7,
            )

            print("✅ Grok response received.")
            return content

        except httpx.ReadTimeout:
            print(f"⏳ Timeout on attempt {attempt}/{len(timeouts)}")

        except Exception as e:
            print("❌ Grok error:", str(e))
            # Only retry on first 2 attempts
            if attempt < len(timeouts):
                continue
            else:
                # Fully failed after retries
                return (
                    "I'm having trouble contacting my intelligence engine right now. "
                    "Please try again in a few seconds!"
                )

    # Should never hit here
    return "Something unexpected happened. Please try again!"

# --------------------------
# In-memory DB (placeholder until Supabase)
# --------------------------

_fake_db: dict[str, TwinProfile] = {}


async def load_profile(user_id: str) -> TwinProfile:
    if user_id in _fake_db:
        return _fake_db[user_id]

    profile = TwinProfile(
        user_id=user_id,
        display_name=None,
        tone="insightful",
        creativity=0.7,
        favorite_topics=[],
        last_updated=datetime.utcnow(),
    )
    _fake_db[user_id] = profile
    return profile


async def save_profile(profile: TwinProfile):
    profile.last_updated = datetime.utcnow()
    _fake_db[profile.user_id] = profile


# --------------------------
# Generate Twin Output (FIXED)
# --------------------------
@router.post("/generate")
async def generate_twin_output(
    body: TwinGenerateRequest,
    user=Depends(verify_supabase_token),   # <-- authenticated user object
):
    """
    Generate output using the user's Synthetic Twin
    """
    # FIX: Supabase returns "id", not "user_id"
    if "id" not in user:
        raise HTTPException(401, "Invalid authentication payload")

    user_id = user["id"]
    print("🔐 Authenticated user id:", user_id)

    # Load full memory graph
    memory_graph =  load_memories(user_id)

    # Load twin profile for authenticated user
    profile = await load_profile(user_id)

   # Build system + user messages for Grok
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI synthetic twin. You learn continuously from the user. "
                "You maintain personality traits, goals, and long-term memory. "
                "Use the memory provided below to respond.\n\n"
                f"MEMORY:\n{memory_graph}\n"
            ),
        },
        {"role": "user", "content": body.prompt},
    ]

    # Call Grok with safe retry wrapper
    content = await safe_llm_generate(messages)

    # Save memory (the final improved memory system is already enabled)
    save_memory(user_id, body.prompt, content)

    return {"response": content}

# --------------------------
# Fetch Twin Profile
# --------------------------
@router.get("/profile", response_model=TwinProfileResponse)
async def get_twin_profile(user=Depends(get_current_user)):
    user_id = user["id"]
    print("📥 Loading profile for:", user_id)
    # Load or create TwinProfile from our in-memory store
    profile = await load_profile(user_id)
    # Ensure some friendly defaults
    if not profile.display_name:
        profile.display_name = "Your AI Twin"
    if profile.favorite_topics is None:
        profile.favorite_topics = []

    # FastAPI + Pydantic will handle serialization
    return TwinProfileResponse(profile=profile)


# --------------------------
# Update Twin Profile
# --------------------------
@router.post("/profile", response_model=TwinProfileResponse)
async def update_twin_profile(body: TwinProfileUpdate, user=Depends(get_current_user)):
    user_id = user["id"]
    profile = await load_profile(user_id)

    if body.display_name is not None:
        profile.display_name = body.display_name
    if body.tone is not None:
        profile.tone = body.tone
    if body.creativity is not None:
        profile.creativity = body.creativity
    if body.favorite_topics is not None:
        profile.favorite_topics = body.favorite_topics

    await save_profile(profile)
    return TwinProfileResponse(profile=profile)
