# app/services/video_service.py

import re
import json
from typing import List

from app.services.video_planner import SceneModel
from app.services.video_renderer import render_video_to_supabase


# ------------------------------------------------------------
# UTILITIES
# ------------------------------------------------------------

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using punctuation marks."""
    sentence_regex = r"(?<=[.!?])\s+"
    parts = re.split(sentence_regex, text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 0]


def estimate_duration(text: str) -> int:
    """
    Duration: ~0.33 seconds per word, clamped between 4 and 10 seconds.
    """
    words = len(text.split())
    duration = int(words * 0.33)
    return max(4, min(10, duration))


def caption_trim(text: str, max_words: int = 14) -> str:
    """
    Trim to short caption for on-screen display.
    """
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "…"


def parse_script_json(script_json: str) -> str:
    """
    Convert LLM script JSON into plain text:
    - Title
    - Headings
    - Paragraphs
    If invalid JSON, return the raw text.
    """
    try:
        data = json.loads(script_json)
    except Exception:
        return script_json

    if isinstance(data, dict) and "sections" in data:
        blocks: List[str] = []
        title = data.get("title", "").strip()
        if title:
            blocks.append(title)

        for sec in data["sections"]:
            heading = (sec.get("heading") or "").strip()
            content = (sec.get("content") or "").strip()
            if heading:
                blocks.append(heading)
            if content:
                blocks.append(content)

        return "\n\n".join(blocks)

    if isinstance(data, list):
        return "\n\n".join(str(item) for item in data)

    return script_json


# ------------------------------------------------------------
# SCENE GENERATION
# ------------------------------------------------------------

def extract_scenes_from_script(script_json: str) -> List[SceneModel]:
    """
    Convert a full YouTube script into several scenes:
    - Parse JSON → plain text
    - Split into paragraphs, then sentences
    - Trim captions, estimate durations
    """

    full_text = parse_script_json(script_json)

    # Split on new lines for paragraphs
    paragraphs = [p.strip() for p in full_text.split("\n") if p.strip()]

    scenes: List[SceneModel] = []
    scene_id = 1

    for block in paragraphs:
        sentences = split_into_sentences(block)
        for sentence in sentences:
            if not sentence or len(sentence) < 2:
                continue
            caption = caption_trim(sentence, max_words=14)
            duration = estimate_duration(sentence)

            scenes.append(
                SceneModel(
                    id=scene_id,
                    caption=caption,
                    duration_sec=duration,
                    background_image_url=None
                )
            )
            scene_id += 1

    if not scenes:
        scenes = [SceneModel(id=1, caption="Your video", duration_sec=8)]

    return scenes


# ------------------------------------------------------------
# MAIN VIDEO BUILDER
# ------------------------------------------------------------

# def build_youtube_video_from_script(
#     script_json: str,
#     with_music: bool = False,
# ) -> tuple[List[SceneModel], str]:
#     """
#     Convert script → scenes → video, and return both scenes and final video URL.
#     """
#     scenes = extract_scenes_from_script(script_json)

#     video_url = render_video_to_supabase(
#         scenes=scenes,
#         with_voiceover=False,
#     )

#     return scenes, video_url
