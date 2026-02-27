from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_templates():
    return [
        # General content templates
        {"id": 1,  "title": "Blog Post",                    "category": "general",    "credit_cost": 5},
        {"id": 2,  "title": "Product Description",          "category": "general",    "credit_cost": 5},
        {"id": 3,  "title": "Social Media Post",            "category": "general",    "credit_cost": 2},
        {"id": 4,  "title": "Email",                        "category": "general",    "credit_cost": 2},
        {"id": 5,  "title": "Report",                       "category": "general",    "credit_cost": 5},
        # Ecommerce SEO templates
        {"id": 10, "title": "Ecommerce Product Description","category": "ecommerce",  "credit_cost": 5},
        {"id": 11, "title": "Ecommerce Blog Post",          "category": "ecommerce",  "credit_cost": 5},
        {"id": 12, "title": "Marketplace Listing",          "category": "ecommerce",  "credit_cost": 6},
        {"id": 13, "title": "Category Page",                "category": "ecommerce",  "credit_cost": 4},
        {"id": 14, "title": "Product FAQ",                  "category": "ecommerce",  "credit_cost": 3},
        {"id": 15, "title": "Meta Tags",                    "category": "ecommerce",  "credit_cost": 2},
    ]
