from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.llm import generate_muse_response
from pydantic import BaseModel
from uuid import UUID

router = APIRouter()

class MusePrompt(BaseModel):
    user_id: UUID
    prompt: str

@router.post("/chat")
def muse_chat(prompt_req: MusePrompt, db: Session = Depends(get_db)):
    response = generate_muse_response(prompt_req.user_id, prompt_req.prompt)
    return {"muse_response": response}
