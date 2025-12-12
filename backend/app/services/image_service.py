# app/services/image_service.py

import os
import requests
from typing import Optional
from pathlib import Path
from openai import OpenAI
import uuid

# Use Supabase service for direct file upload
# NOTE: We need to use the Supabase client directly here,
# which requires similar setup to supabase_service.py
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_IMAGE_BUCKET", "images") # Assuming an 'images' bucket

# Initialize OpenAI client
client: Optional[OpenAI] = None
if os.getenv("MODEL_API_KEY"):
    client = OpenAI(api_key=os.getenv("MODEL_API_KEY"))
else:
    print("[OPENAI] MODEL_API_KEY is missing. DALL-E service will not work.")

# Initialize Supabase client
supabase_client: Client | None = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    except Exception as e:
        print(f"[SUPABASE] ERROR initializing Supabase client in image_service: {e}")


def _upload_file_to_supabase(local_path: Path, user_id: str) -> str:
    """Uploads a file to Supabase storage and returns the public URL."""
    if supabase_client is None:
        raise RuntimeError("Supabase client not initialized for upload.")
    
    # Define the remote path for the image
    file_extension = local_path.suffix
    remote_file_name = f"{user_id}/{uuid.uuid4().hex}{file_extension}"
    
    with open(local_path, "rb") as f:
        # Upload the file to the specified bucket
        resp = supabase_client.storage.from_(SUPABASE_BUCKET).upload(
            file=f,
            path=remote_file_name,
            file_options={"content-type": "image/png"}
        )
        
    # Get the public URL
    url_resp = supabase_client.storage.from_(SUPABASE_BUCKET).get_public_url(remote_file_name)
    
    # Clean up local file
    try:
        os.remove(local_path)
    except OSError:
        pass # Ignore errors if file is already gone

    return url_resp


def generate_ai_image_and_upload(
    prompt: str, user_id: str, aspect_ratio: str = "1024x1792"
) -> str:
    """
    Generates a DALL-E image, saves it locally, uploads it to Supabase, 
    and returns the public URL.
    """
    if client is None:
        raise RuntimeError("OpenAI client not initialized (check MODEL_API_KEY).")

    print(f"[AI SERVICE] Generating image for prompt: '{prompt[:50]}...'")
    local_path = Path(f"/tmp/img_{uuid.uuid4().hex}.png")

    try:
        # 1. Generate the image
        response = client.images.generate(
            model="dall-e-3", 
            size=aspect_ratio,
            prompt=prompt,
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url

        # 2. Download the generated image to a temporary local file
        image_data = requests.get(image_url).content
        with open(local_path, "wb") as f:
            f.write(image_data)
        
        # 3. Upload to Supabase and get the final public URL
        public_url = _upload_file_to_supabase(local_path, user_id)
        
        print(f"[AI SERVICE] Image uploaded to: {public_url}")
        return public_url

    except Exception as e:
        print(f"❌ [AI SERVICE] Image generation/upload failed: {e}")
        # Clean up local file on error
        if local_path.exists():
             os.remove(local_path)
        raise RuntimeError(f"Image generation failed: {e}")