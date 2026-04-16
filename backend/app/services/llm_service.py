import os
from typing import Optional
from pathlib import Path
import httpx
from openai import OpenAI
from app.config import settings
from app.core.costs import get_cost
from app.services.deduplication_service import deduplicator, uniqueness_enhancer

# ---------------------------
# Configuration
# ---------------------------
client: Optional[OpenAI] = None
if os.getenv("MODEL_API_KEY"):
    client = OpenAI(api_key=os.getenv("MODEL_API_KEY"))
else:
    print("[OPENAI] MODEL_API_KEY is missing. AI services will not work.")
# ---------------------------------------------
# Image Generation Function (DALL-E 3)
# ---------------------------------------------
def generate_ai_image(prompt: str, local_path: Path) -> Optional[Path]:
    """
    Calls the DALL-E API to generate an image and saves it to a local file.
    
    This function uses DALL-E 3 and is optimized for the vertical (16:9) 
    aspect ratio used in your video renderer.
    """
    if client is None:
        raise RuntimeError("OpenAI client not initialized (check MODEL_API_KEY).")

    print(f"[AI SERVICE] Generating image for prompt: '{prompt[:50]}...'")

    try:
        response = client.images.generate(
            model="dall-e-3", 
            # Aspect ratio suitable for vertical video (1024x1792 is a supported DALL-E 3 size)
            size="1024x1792", 
            prompt=prompt,
            quality="standard",
            n=1,
        )
    except Exception as e:
        print(f"[AI SERVICE] DALL-E API Error: {e}")
        raise RuntimeError("AI image generation API call failed.")

    # 1. Get the image URL from the response
    image_url = response.data[0].url

    if not image_url:
        raise RuntimeError("DALL-E returned no image URL.")

    # 2. Download the image and save it locally
    response = requests.get(image_url)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to download image from URL: {response.status_code}")

    with open(local_path, "wb") as f:
        f.write(response.content)

    print(f"[AI SERVICE] Image saved to {local_path.as_posix()}")
    return local_path

 # ------------------------------------------------------
# X.ai Grok-4 Chat Client for Synth Twin + SynthCore
# ------------------------------------------------------

class XaiClient:
    """
    Universal client for Grok-4 API used by the Synth Twin.
    Required method: chat(system_prompt, user_prompt, creativity)
    """

    def __init__(self):
        self.api_key = settings.XAI_API_KEY
        self.base_url = settings.XAI_API_BASE or "https://api.x.ai/v1"
        self.model = settings.model_name or "grok-4"

        if not self.api_key:
            print("[XAI CLIENT] ERROR: Missing XAI_API_KEY - LLM will not work.")

    async def chat(self, system_prompt: str, user_prompt: str, creativity: float = 0.7):
        """
        Required interface for SynthCore.
        Makes a Grok-4 chat completion call.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "temperature": creativity,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        print("\n--- XAI CLIENT DEBUG ---")
        print("[XAI] Model:", self.model)
        print("[XAI] Base URL:", self.base_url)
        print("[XAI] Creativity:", creativity)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )

        if response.status_code != 200:
            print("[XAI ERROR]", response.text)
            raise Exception(f"Grok API Error {response.status_code}: {response.text}")

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return content.strip()


# Instantiate global client
llm_client = XaiClient()

print("[OK] XAI Grok Client initialized as llm_client")
   
# ---------------------------\
# Main LLM function
# ---------------------------\
async def get_llm_response(prompt: str):
    """Compatibility wrapper for twin.py"""
    return await generate_llm_content(prompt, "General Content")

async def generate_llm_content(prompt: str, template: str, user_id: str = "anonymous"):
    """
    Send prompt + template to LLM and return cleaned text.
    Ensures unique content by tracking generation history and adjusting parameters.
    """
    
    # Track how many times this prompt has been generated recently
    variation_count = deduplicator.get_variations_required(user_id, prompt, template)
    
    # Augment prompt with uniqueness instructions if this is a repeat
    augmented_prompt = uniqueness_enhancer.augment_prompt(prompt, variation_count)
    
    # Adjust temperature for uniqueness
    base_temp = 0.7
    adjusted_temp = uniqueness_enhancer.adjust_temperature(base_temp, variation_count)
    
    system_message = (
        "You are an expert content writer. "
        f"Write content using template: {template}. "
        "Return plain text only—no JSON or extra formatting."
    )

    payload = {
        # Use the property for consistent access
        "model": settings.model_name, 
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": augmented_prompt},
        ],
        "temperature": adjusted_temp,
    }

    headers = {
        "Authorization": f"Bearer {settings.XAI_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # [*] DEBUG STEP 1: Print Config Check
    print("\n--- LLM API DEBUG START ---")
    print(f"[LLM DEBUG] Base URL: {settings.XAI_API_BASE}")
    print(f"[LLM DEBUG] API Key Check: {'SET' if settings.XAI_API_KEY and len(settings.XAI_API_KEY)>10 else 'MISSING/TOO SHORT'}")
    print(f"[LLM DEBUG] Model: {settings.model_name}")
    print(f"[LLM DEBUG] Variation Count: {variation_count} | Base Temp: {base_temp} → Adjusted Temp: {adjusted_temp}")
    
    # Note: Payload includes the full prompt, which can be long.
    # print(f"[LLM DEBUG] Payload: {payload}\n") 
    
    try:
        # Timeout increased for LLM calls
        async with httpx.AsyncClient(base_url=settings.XAI_API_BASE, timeout=90.0) as client:
            response = await client.post("/chat/completions", json=payload, headers=headers)
    
    # [*] DEBUG STEP 2: Catch Network/Connection Errors
    except httpx.RequestError as e:
        print(f"[LLM FAILURE] HTTPX Request Error: Could not connect to {settings.XAI_API_BASE}. Error: {e}")
        # Re-raise the exception with a clear message
        raise Exception(f"Network request to LLM failed: {e}")        

    # [*] DEBUG STEP 3: Check API Status Code (Authorization, Bad Request, etc.)
    if response.status_code != 200:
        print(f"[LLM FAILURE] API Status: {response.status_code}")
        # Print the API's error body for max detail
        print(f"[LLM FAILURE] API Response: {response.text}") 
        # Re-raise the exception with a clear message
        raise Exception(f"LLM API Error {response.status_code}: {response.text}")

    # Success: Parse and return
    data = response.json()
    raw_text = data["choices"][0]["message"]["content"]
    
    # Apply post-processing for uniqueness
    processed_content = uniqueness_enhancer.post_process_for_uniqueness(raw_text.strip(), "text")
    
    # Track this generation for deduplication
    deduplicator.track_generation(
        user_id=user_id,
        prompt=prompt,
        template=template,
        content=processed_content,
        content_type="text",
    )
    
    print(f"[LLM DEBUG] Status: SUCCESS | Content processed for uniqueness")
    print("--- LLM API DEBUG END ---\n")
    
    return processed_content
