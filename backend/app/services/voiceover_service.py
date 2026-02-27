# app/services/voiceover_service.py

import os
from pathlib import Path
from typing import List, Optional


from app.services.video_planner import SceneModel

OPENAI_API_KEY = os.getenv("MODEL_API_KEY")
BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUDIO_DIR = BASE_DIR / "tmp" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def synthesize_voice_openai(text: str, output_path: Path, voice: str = "alloy"):
    """
    Example TTS using OpenAI's /v1/audio/speech endpoint.
    You can replace this with xAI's TTS API when available.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set for TTS")

    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    json_payload = {
        "model": "gpt-4o-mini-tts",  # choose a valid TTS model
        "voice": voice,
        "input": text,
        "format": "mp3",
    }

    resp = requests.post(url, headers=headers, json=json_payload, stream=True)
    resp.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def generate_scene_audio_files(
    scenes: List[SceneModel],
    use_voiceover: bool = True,
    voice: str = "alloy",
) -> List[Optional[Path]]:
    """
    For each scene, synthesize voiceover audio (if enabled).
    Returns list of Paths (or None) parallel to scenes.
    """
    audio_paths: List[Optional[Path]] = []
   # When xAI provides a TTS endpoint, you’d replace synthesize_voice_openai with synthesize_voice_xai, keeping the same interface.
    for scene in scenes:
        if use_voiceover and scene.voiceover:
            out_path = AUDIO_DIR / f"scene_{scene.id}.mp3"
            synthesize_voice_openai(scene.voiceover, out_path, voice=voice)
            audio_paths.append(out_path)
        else:
            audio_paths.append(None)

    return audio_paths
