# app/api/youtube_video.py

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel


from app.services.llm_service import get_llm_response
#from app.services.video_service import build_youtube_video_from_script

router = APIRouter(prefix="/api/youtube", tags=["YouTube"])


class VideoRequest(BaseModel):
    topic: str
    style: str = "informative"
    with_music: bool = False

@router.post("/upload-image")
async def upload_image(file: UploadFile):
    ext = file.filename.split(".")[-1]
    fname = f"upload_{uuid4().hex}.{ext}"
    path = f"static/uploads/{fname}"
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    return {"url": f"/static/uploads/{fname}"}


# @router.post("/video")
# def generate_youtube_video(req: VideoRequest):
#     """
#     Generate long-form YouTube video from topic:
#     1) Create script
#     2) Convert script → scenes
#     3) Render video using the new renderer
#     """
#     script_prompt = f"""
# Create a full YouTube video script.

# Topic: {req.topic}
# Style: {req.style}

# Structure:
# - Hook (first 5 seconds)
# - Intro
# - 3–6 main sections with timestamps
# - Clear call to action
# - Short, spoken-style sentences
# """

#     try:
#         # 1) generate script
#         script = get_llm_response(script_prompt)

#         # 2) script -> scenes -> video
#         scenes, video_url = build_youtube_video_from_script(
#             script_json=script,
#             with_music=req.with_music,
#         )

#         return {
#             "topic": req.topic,
#             "script": script,
#             "scenes": [s.dict() for s in scenes],
#             "video_url": video_url,
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Video generation error: {e}")
