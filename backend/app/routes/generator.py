from app.db.models import User
from fastapi import APIRouter, Depends, HTTPException
from app.routes.schemas import GenerateSchema
from app.services.llm_service import generate_llm_content
from app.services.security import get_current_user
from app.services.supabase_service import deduct_credits
from app.core.costs import get_cost

router = APIRouter()

@router.post("/")
async def generate_content(request: GenerateSchema):
   # user_id = current_user.id

    # cost calculation
    cost = get_cost(request.template)

    # deduct credits
    #try:
    #    deduct_credits(user_id, cost)
    #except ValueError as e:
    #    raise HTTPException(status_code=402, detail=str(e))

    # LLM generation
    try:
        content = await generate_llm_content(request.prompt, request.template)
        return {"content": content}
    except Exception as e:
        print("[ERROR] Error generating content:", e)
        raise HTTPException(status_code=500, detail="LLM generation failed")
