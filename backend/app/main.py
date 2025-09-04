from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import generator, templates

app = FastAPI(title="Content & Blog Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generator.router, prefix="/api/generator", tags=["generator"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])

@app.get("/")
def root():
    return {"message": "Content & Blog Generator API is running"}
