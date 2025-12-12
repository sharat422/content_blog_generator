# app/services/video_pipeline.py

import os
import json
import uuid
from typing import List, Optional
from pathlib import Path

from moviepy.editor import (
    TextClip,
    ColorClip,
    CompositeVideoClip,
    concatenate_videoclips,
    AudioFileClip,
)
from pydantic import BaseModel

from app.services.llm import get_llm_response  # you already have this

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static"
VIDEO_DIR = STATIC_DIR / "videos"

VIDEO_DIR.mkdir(parents=True, exist_ok=True)


class SceneModel(BaseModel):
    id: int
    caption: str
    voiceover: Optional[str] = None
    duration_sec: int = 5


def plan_scenes(topic: str, style: str = "informative") -> List[SceneModel]:
    """
    Ask the LLM to break the topic into structured scenes for video.
    """

    prompt = f"""
You are a YouTube video director.

Create 4–8 short scenes for a vertical video.

Topic: "{topic}"
Style: "{style}"

Return ONLY valid JSON like:
[
  {{"id": 1, "caption": "On-screen text max 15 words", "voiceover": "spoken version", "duration_sec": 5}},
  ...
]
"""

    raw = get_llm_response(prompt)

    try:
        start = raw.find("[")
        end = raw.rfind("]")
        if start != -1 and end != -1:
            raw = raw[start : end + 1]
        data = json.loads(raw)
    except Exception:
        # Fallback: 1 scene if parsing fails
        data = [
            {
                "id": 1,
                "caption": topic,
                "voiceover": topic,
                "duration_sec": 10,
            }
        ]

    scenes = [SceneModel(**item) for item in data]
    return scenes


def build_video(
    scenes: List[SceneModel],
    output_name: Optional[str] = None,
    bg_color=(10, 10, 30),
    text_color="white",
    size=(1080, 1920),
    font_size=60,
    fps: int = 30,
    background_music_path: Optional[str] = None,
) -> str:
    """
    Build a simple vertical video from scenes.
    (One “slide” per scene with text; can be extended with images/tts later.)
    """

    clips = []

    for scene in scenes:
        bg = ColorClip(size, color=bg_color, duration=scene.duration_sec)

        txt = TextClip(
            scene.caption,
            fontsize=font_size,
            color=text_color,
            method="caption",
            size=(int(size[0] * 0.9), None),
        ).set_duration(scene.duration_sec)

        txt = txt.set_position("center")

        comp = CompositeVideoClip([bg, txt])
        clips.append(comp)

    final_clip = concatenate_videoclips(clips, method="compose")

    if background_music_path and os.path.exists(background_music_path):
        audio = AudioFileClip(background_music_path).volumex(0.5)
        audio = audio.set_duration(final_clip.duration)
        final_clip = final_clip.set_audio(audio)

    if not output_name:
        output_name = f"video_{uuid.uuid4().hex}.mp4"

    output_path = VIDEO_DIR / output_name

    final_clip.write_videofile(
        output_path.as_posix(),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        verbose=False,
        logger=None,
    )

    final_clip.close()
    for c in clips:
        c.close()

    # Return relative path like "static/videos/xxx.mp4"
    rel_path = output_path.relative_to(BASE_DIR).as_posix()
    return rel_path
