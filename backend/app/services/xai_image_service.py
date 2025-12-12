# app/services/xai_image_service.py

from pathlib import Path
from PIL import Image, ImageDraw
import uuid

BASE_IMAGE_DIR = Path("static/scene_images")
BASE_IMAGE_DIR.mkdir(parents=True, exist_ok=True)


class XAIImageError(Exception):
    pass


def generate_xai_image(prompt: str) -> Path:
    """
    Placeholder AI generator (works even without API keys).
    Creates a simple image so pipeline is verified.
    """
   filename = f"ai_bg_{uuid.uuid4().hex}.jpg"
    out_path = BASE_IMAGE_DIR / filename

    img = Image.new("RGB", (1080, 1920), color=(40, 40, 80))
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), f"AI BG: {prompt[:40]}...", fill=(255, 255, 255))
    img.save(out_path)

    return out_path
