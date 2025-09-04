import httpx
import logging
import json
from typing import List, Dict
from ..core.config import settings

class GenerationError(Exception):
    pass

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def llm_complete(messages: List[Dict], model: str | None = None) -> str:
    model = model or settings.model_name
    headers = {
        "Authorization": f"Bearer {settings.model_api_key}",
        "Content-Type": "application/json",
    }

    payload = {"model": model, "messages": messages, "temperature": 0.7}

    logger.debug("Sending request to LLM...")
    logger.debug("Payload: %s", json.dumps(payload, indent=2))

    try:
        async with httpx.AsyncClient(base_url=settings.model_base_url, timeout=90.0) as client:
            response = await client.post("/chat/completions", json=payload, headers=headers)

        if response.status_code >= 400:
            logger.error("LLM error: %s", response.text)
            raise GenerationError(f"LLM error {response.status_code}: {response.text}")

        response_json = response.json()
        raw_content = response_json["choices"][0]["message"]["content"].strip()
        logger.debug("Raw content from LLM: %s", raw_content)

        # Ensure valid JSON
        try:
            json.loads(raw_content)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON from LLM, wrapping in fallback")
            fallback = {
                "title": "Untitled",
                "sections": [{"heading": "", "content": raw_content}]
            }
            raw_content = json.dumps(fallback)

        return raw_content

    except httpx.RequestError as e:
        logger.exception("Request to LLM failed")
        raise GenerationError(f"Request failed: {e}") from e
    except Exception as e:
        logger.exception("Unexpected error in llm_complete")
        raise
