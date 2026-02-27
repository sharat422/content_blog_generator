from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
import os
import json

from app.services.security import verify_supabase_token
from app.services.supabase_service import supabase, deduct_credits

router = APIRouter(prefix="/api/journeys", tags=["Journeys"])

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class JourneyCreateSchema(BaseModel):
    goal: str
    timeframe: str
    model: str  # gemini-1.5-flash or gemini-1.5-pro

@router.post("/generate")
async def generate_journey(body: JourneyCreateSchema, user=Depends(verify_supabase_token)):
    user_id = user["id"]
    
    # 1. Deduct Credits (Roadmap generation cost)
    # Reusing your existing credit system
    try:
        deduct_credits(user_id, cost=100) # Example cost
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))

    # 2. Call Gemini
    model_name = body.model if body.model.startswith("gemini") else "gemini-1.5-flash"
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    Create a detailed learning roadmap for: "{body.goal}" in "{body.timeframe}".
    Return ONLY a JSON object matching this structure:
    {{
      "title": "string",
      "description": "string",
      "category": "string",
      "milestones": [
        {{ "id": "m1", "title": "string", "steps": [{{ "id": "s1", "title": "string", "completed": false }}] }}
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean the response if AI includes markdown code blocks
        clean_json = response.text.strip().replace("```json", "").replace("```", "")
        journey_data = json.loads(clean_json)
        
        # 3. Save to Supabase
        journey_data["user_id"] = user_id
        res = supabase.table("journeys").insert(journey_data).execute()
        
        return res.data[0]
    except Exception as e:
        print(f"Gemini Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate roadmap")

@router.get("/")
async def get_journeys(user=Depends(verify_supabase_token)):
    res = supabase.table("journeys").select("*").eq("user_id", user["id"]).order("created_at", desc=True).execute()
    return res.data

@router.patch("/{journey_id}")
async def update_journey(journey_id: str, updates: dict, user=Depends(verify_supabase_token)):
    # Security: Ensure user owns the journey
    res = supabase.table("journeys").update(updates).eq("id", journey_id).eq("user_id", user["id"]).execute()
    return res.data
