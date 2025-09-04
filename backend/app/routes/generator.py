from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm import llm_complete
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

class GenerateRequest(BaseModel):
    prompt: str
    template: str = "Blog Post"


TEMPLATE_INSTRUCTIONS = {
    "Blog Post": "Write a detailed blog post with an introduction, body sections, and conclusion. Use paragraphs, bullet points, and markdown formatting.",
    "Product Description": "Write a persuasive product description highlighting key features, benefits, and use cases. Keep it engaging and clear.",
    "Social Media Post": "Write a catchy and engaging social media post. Keep it short, conversational, and attention-grabbing.",
    "Email": "Write a professional email with a greeting, body, and closing. Make it clear, concise, and polite.",
    "Report": "Write a structured report with sections, key findings, and recommendations."
}

@router.post("/")
async def generate_content(req: GenerateRequest):
    logger.debug("Received request: %s", req.dict())

    template_instruction = TEMPLATE_INSTRUCTIONS.get(
        req.template, 
        "Write structured, professional content."
    )

    messages = [
        {
            "role": "system",
            "content": (
                f"You are an expert content writer. Write content using template: {template_instruction}. "
                "Return plain text only, without any JSON structure, headings, brackets, or extra quotes. "
                "Separate paragraphs with line breaks. "
                "Ensure the content is readable, structured, and professional."
            )
            
        },
        {"role": "user", "content": req.prompt}
    ]

    try:
        raw_content = await llm_complete(messages)

        # Ensure valid JSON
        try:
            structured_content = json.loads(raw_content)
        except json.JSONDecodeError:
            logger.warning("LLM returned invalid JSON, wrapping in fallback structure")
            structured_content = {
                "title": "Untitled",
                "sections": [{"heading": "", "content": raw_content}]
            }

        return {"content": structured_content}

    except Exception as e:
        logger.exception("❌ Error generating content")
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")
