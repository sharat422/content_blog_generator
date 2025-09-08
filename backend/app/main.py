from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import generator, templates
import os

app = FastAPI(title="Content & Blog Generator")

origins = [
    "https://www.writeswift.ai",   # production frontend
    "http://localhost:5173",       # local dev (Vite default)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generator.router, prefix="/api/generator", tags=["generator"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])

@app.get("/")
def root():
    return {"message": "Content & Blog Generator API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
