# app/api/image.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import os
import uuid
from pathlib import Path

# --- NEW IMPORTS ---
from app.services.security import verify_supabase_token
from app.services.supabase_service import (
    deduct_credits,
    COST_IMAGE_GEN_BASIC, # Use the new cost constant
    supabase,
)
from app.services.llm_service import generate_ai_image # Use the service you created

# --- Setup Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TMP_DIR = BASE_DIR / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)
# Ensure this environment variable is set
SUPABASE_BUCKET = os.getenv("SUPABASE_IMAGE_BUCKET", "imageswift") 

router = APIRouter(prefix="/api/image", tags=["Image Generation"])

class ImageGenerationRequest(BaseModel):
    """Defines the input for a single image generation."""
    prompt: str

@router.post("/generate")
def generate_image_route(
    request: ImageGenerationRequest,
    user=Depends(verify_supabase_token),
):
    """
    Handles image generation request:
    1. Authenticates user.
    2. Checks/Deducts credits.
    3. Triggers DALL-E image generation.
    4. Uploads result to Supabase Storage.
    5. Returns public URL and new credit balance.
    """
    user_id = user["id"]
    cost = COST_IMAGE_GEN_BASIC

    # 1. Deduct Credits
    try:
        new_balance = deduct_credits(user_id, cost)
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e)) # 402 for payment required
    except Exception as e:
        raise HTTPException(status_code=500, detail="Credit deduction failed.")

    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase service not configured.")

    # 2. Prepare temporary file paths
    unique_id = uuid.uuid4().hex
    # DALL-E 3 default is PNG, but we'll use PNG for lossless upload
    final_name = f"image_{unique_id}.png"
    temp_path = TMP_DIR / final_name

    try:
        # 3. Generate Image
        generate_ai_image(
            prompt=request.prompt,
            local_path=temp_path,
        )

        # 4. Upload to Supabase Storage
        storage_path = f"generated/{final_name}"

        with open(temp_path, "rb") as f:
            supabase.storage.from_(SUPABASE_BUCKET).upload(
                storage_path,
                f,
                {"content-type": "image/png", "x-upsert": "true"},
            )

        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)

        # 5. Cleanup local file
        os.remove(temp_path)

        return {
            "public_url": public_url,
            "new_credit_balance": new_balance,
            "message": "Image generated and uploaded successfully."
        }

    except Exception as e:
        print(f"Error during image generation/upload: {e}")
        # IMPORTANT: In a production app, you should also implement a credit refund here
        raise HTTPException(status_code=500, detail="Image generation failed.")
