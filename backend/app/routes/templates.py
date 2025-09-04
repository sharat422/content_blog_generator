from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_templates():
    return [{"id": 1, "title": "Blog Post"}, {"id": 2, "title": "Product Description"}]
