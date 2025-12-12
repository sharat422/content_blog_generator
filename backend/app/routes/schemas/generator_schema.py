from pydantic import BaseModel

class GenerateSchema(BaseModel):
    prompt: str
    template: str
