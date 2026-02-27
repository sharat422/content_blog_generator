# app/services/video_planner.py - UPDATED

import json
from pydantic import BaseModel
from typing import List, Optional

from app.services.llm_service import get_llm_response

class SceneModel(BaseModel):
    id: int
    caption: str
    duration_sec: int
    voiceover: Optional[str] = None
    background_image_url: str | None = None
    # NEW: Field for the AI image prompt
    image_prompt: str | None = None 


def generate_video_plan(topic: str, style: str = "informative") -> List[SceneModel]:
    """
    Generates short-form scenes for Shorts/Reels using the LLM.
    """

    prompt = f"""
You are planning a short-form vertical video.

Topic: "{topic}"
Style: "{style}"

Return JSON EXACTLY like this:
{{
  "scenes": [
    {{ 
        "caption": "AI text...", 
        "duration_sec": 5, 
        "image_prompt": "A cinematic, vertical photo of a futuristic AI interface." 
    }},
    {{ 
        "caption": "Another line...", 
        "duration_sec": 6, 
        "image_prompt": "A close-up of a person typing excitedly on a keyboard." 
    }}
  ]
}}

Rules:
- 4 to 8 scenes
- caption must be short and readable on mobile
- duration_sec between 4 and 7
- **image_prompt MUST be a detailed, creative, English description suitable for a photorealistic AI image generator (DALL-E 3).**
- DO NOT include commentary outside JSON
"""

    response = get_llm_response(prompt)

    try:
        data = json.loads(response)
    except Exception:
        # fallback if model did not return JSON
        return [
            SceneModel(id=1, caption="Unable to parse scene plan", duration_sec=6, image_prompt=topic)
        ]

    raw_scenes = data.get("scenes", [])

    scenes: List[SceneModel] = []
    for idx, item in enumerate(raw_scenes, start=1):
        caption = (item.get("caption") or topic).strip()
        duration = item.get("duration_sec") or 5
        # NEW: Extract image_prompt, falling back to caption if missing
        image_prompt = item.get("image_prompt")

        scenes.append(
            SceneModel(
                id=idx,
                caption=caption,
                duration_sec=duration,
                image_prompt=image_prompt, # Store the LLM'S prompt
                # Ensure existing fields are also passed or defaulted
                background_image_url=None
            )
        )
    return scenes
