# app/routes/schemas.py

from pydantic import BaseModel

class GenerateSchema(BaseModel):
    prompt: str
    template: str | None = "Blog Post"
