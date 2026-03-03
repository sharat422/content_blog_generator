from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import os
from fastapi.staticfiles import StaticFiles

import os
load_dotenv()

from app.api import twin, auth, youtube_video, video, billing, credits, billing_plan, ecommerce, chatbot
from app.routes import generator, templates

app = FastAPI(title="Content & Blog Generator")
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "https://www.writeswift.ai",
    "https://writeswift.ai",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# static for videos
#app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(generator.router, prefix="/api/generator", tags=["generator"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(video.router)
app.include_router(youtube_video.router)
app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(credits.router)
app.include_router(billing_plan.router)
app.include_router(ecommerce.router)
app.include_router(twin.router, prefix="/api/twin", tags=["Twin"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["chatbot"])

@app.get("/")
def root():
    return {"message": "Content & Blog Generator API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
