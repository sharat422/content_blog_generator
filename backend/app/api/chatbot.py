from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm_service import llm_client

router = APIRouter()

class ChatMessage(BaseModel):
    message: str

@router.post("/")
async def chat(request: ChatMessage):
    try:
        system_prompt = (
            "You are a helpful customer support assistant for WriteSwift.ai, an AI content and video generation platform. "
            "Your goal is to politely answer user questions about the platform. "
            "WriteSwift features an AI blog generator, YouTube short / TikTok video generator, Twin API (a personalized AI clone), and an Ecommerce tool. "
            "Keep your answers concise, friendly, and helpful. Do not use markdown."
        )
        # Using a low creativity value (e.g., 0.3) for more deterministic/factual support responses
        response_text = await llm_client.chat(
            system_prompt=system_prompt,
            user_prompt=request.message,
            creativity=0.3
        )
        return {"response": response_text}
    except Exception as e:
        print(f"[CHATBOT ERROR] {e}")
        raise HTTPException(status_code=500, detail="Failed to get a response from the chatbot.")
