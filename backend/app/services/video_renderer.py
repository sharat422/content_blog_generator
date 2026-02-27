# app/services/video_renderer.py

import os
import subprocess
import uuid
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageDraw, ImageFont

# [*] FIX: Use the newly created image_service and remove the redundant IMAGE_COST import
from app.services.image_service import generate_ai_image_and_upload 
from app.services.supabase_service import deduct_credits
from app.config import CREDIT_COSTS

from app.services.video_planner import SceneModel
from app.services.voiceover_service import generate_scene_audio_files

# ------------------------------------------------------------------
# Paths & Supabase config (unchanged)
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TMP_DIR = BASE_DIR / "tmp"
FRAMES_DIR = TMP_DIR / "frames"
SEGMENTS_DIR = TMP_DIR / "segments"

FRAMES_DIR.mkdir(parents=True, exist_ok=True)
SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_VIDEO_BUCKET", "writeswift")

# ... (Supabase client init and _run_ffmpeg utility functions) ...

# ------------------------------------------------------------------
# HELPER: Frame Creation (Updated to support background image URL)
# ------------------------------------------------------------------

def _download_image(url: str, output_path: Path) -> Path:
    """Downloads an image from a URL and saves it locally."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_path

# [*] MODIFIED: _create_frame_image to handle background_image_path
def _create_frame_image(
    text: str,
    output_path: Path,
    background_image_path: Optional[Path] = None,
    size: tuple[int, int] = (1080, 1920),
):
    """Creates a still frame image (1080x1920) with centered text."""
    
    if background_image_path and background_image_path.exists():
        # Load and resize the generated image
        img = Image.open(background_image_path).resize(size)
    else:
        # Fallback to solid black background
        img = Image.new("RGB", size, color=(0, 0, 0))

    d = ImageDraw.Draw(img)
    # Define font (assuming you have a 'arial.ttf' or similar for testing)
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except IOError:
        font = ImageFont.load_default()

    # Simple text wrapping and centering logic
    MAX_WIDTH = size[0] - 100
    caption_lines = []
    current_line = []
    
    # Placeholder:
    caption_lines = [text[i:i+30] for i in range(0, len(text), 30)]

    text_y = (size[1] // 2) - (len(caption_lines) * 50) # Center vertically
    
    for line in caption_lines:
        text_width = d.textlength(line, font=font)
        text_x = (size[0] - text_width) // 2
        d.text((text_x, text_y), line, fill=(255, 255, 255), font=font)
        text_y += 100

    img.save(output_path)
    

# ------------------------------------------------------------------
# HELPER: Asset Generation (Image + Credit Deduction)
# ------------------------------------------------------------------

def _generate_scene_assets(user_id: str, scene: SceneModel) -> Path | None:
    """Generates and uploads the background image for a single scene."""
    if not scene.image_prompt:
        return None # Skip if no prompt is provided

    # Path to save the downloaded/generated image locally for MoviePy/FFMPEG use
    image_path = FRAMES_DIR / f"ai_img_{scene.id}_{uuid.uuid4().hex}.png"
    
    try:
        # 1. Deduct credits for the image generation
        image_cost = CREDIT_COSTS.get("image", 20)
        deduct_credits(user_id, image_cost)
        
        # 2. Generate and upload image
        print(f"[RENDERER] Generating image for scene {scene.id}: {scene.image_prompt[:30]}...")
        # generate_ai_image_and_upload returns the public URL
        image_url = generate_ai_image_and_upload(
            prompt=scene.image_prompt, 
            user_id=user_id,
            aspect_ratio="1024x1792" # Vertical for Shorts/Reels
        )
        scene.background_image_url = image_url
        
        # 3. Download the generated image for local rendering
        local_path = _download_image(image_url, image_path)
        print(f"[RENDERER] Image URL: {image_url}")
        return local_path

    except ValueError as e:
        # Not enough credits
        print(f"[WARN] [RENDERER] Asset generation skipped: {e}")
        # Re-raise the value error to be caught by the API endpoint for 402 status
        raise
    except Exception as e:
        print(f"[ERROR] [RENDERER] Image generation failed for scene {scene.id}: {e}")
        return None
        
        
# ------------------------------------------------------------------
# MAIN RENDERER FUNCTION (MODIFIED)
# ------------------------------------------------------------------
# [*] MODIFIED SIGNATURE to accept user_id and with_music
def render_video_to_supabase(
    user_id: str,
    scenes: List[SceneModel],
    with_voiceover: bool = False,
    with_music: bool = True, # [*] NEW: Control for music
) -> str:
    """
    Renders the video from scenes, handles asset generation, and uploads to Supabase.
    """
    
    # 1. Deduct full video render cost (optional, but recommended for monetization)
    video_cost = CREDIT_COSTS.get("video_render", 100) 
    deduct_credits(user_id, video_cost)
    
    segment_paths: List[Path] = []
    all_audio_paths: List[Optional[Path]] = generate_scene_audio_files(scenes, with_voiceover)
    
    # 2. Process each scene
    for i, scene in enumerate(scenes):
        frame_path = FRAMES_DIR / f"frame_{scene.id}.png"
        segment_path = SEGMENTS_DIR / f"segment_{scene.id}.mp4"
        audio_path = all_audio_paths[i]
        
        # [*] NEW: Generate the AI Image asset (and deducts credits)
        ai_image_path = _generate_scene_assets(user_id, scene) 

        # 3) PIL: Create a still frame image with that background
        _create_frame_image(
            text=scene.caption,
            output_path=frame_path,
            background_image_path=ai_image_path, # Use the REAL AI image path
        )

        # 4) ffmpeg: image + (optional) audio -> mp4
        # (FFMPEG logic remains the same, using frame_path and audio_path)
        if audio_path:
            # ... (Existing FFMPEG command with audio) ...
            cmd = [
                "ffmpeg",
                "-y",
                "-loop", "1",
                "-i", frame_path.as_posix(),
                "-i", audio_path.as_posix(),
                "-c:v", "libx264",
                "-t", str(scene.duration_sec),
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-shortest",
                segment_path.as_posix(),
            ]
        else:
            # ... (Existing FFMPEG command without audio) ...
            cmd = [
                "ffmpeg",
                "-y",
                "-loop", "1",
                "-i", frame_path.as_posix(),
                "-c:v", "libx264",
                "-t", str(scene.duration_sec),
                "-pix_fmt", "yuv420p",
                segment_path.as_posix(),
            ]

        # NOTE: _run_ffmpeg implementation is assumed to be available
        # _run_ffmpeg(cmd)
        segment_paths.append(segment_path)

    # 5) Concatenate all segments
    concat_file = TMP_DIR / f"concat_{uuid.uuid4().hex}.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for seg in segment_paths:
            f.write(f"file '{seg.as_posix()}'\n")

    final_name = f"video_{uuid.uuid4().hex}.mp4"
    final_path = TMP_DIR / final_name

    concat_cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file.as_posix(),
        "-c", "copy",
        final_path.as_posix(),
    ]
    # NOTE: _run_ffmpeg implementation is assumed to be available
    # _run_ffmpeg(concat_cmd)

    # 6) Optional: Add background music (based on with_music flag)
    # The music logic needs to be integrated here if you're using a music file.
    # ... (Music blending logic goes here) ...

    # 7) Upload final video to Supabase
    # ... (Existing upload logic) ...
    # Placeholder for upload:
    video_url = f"https://your.supabase.url/bucket/{final_name}"
    
    return video_url
