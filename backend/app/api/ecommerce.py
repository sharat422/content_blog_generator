"""
ecommerce.py  –  /api/ecommerce router

Provides SEO-optimized content generation tailored for ecommerce sellers.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional

from app.services.security import verify_supabase_token
from app.services.ecommerce_service import generate_ecommerce_content, calculate_seo_score

router = APIRouter(prefix="/api/ecommerce", tags=["Ecommerce"])


# ─────────────────────────────────────────────────────────────
# Request / Response schemas
# ─────────────────────────────────────────────────────────────

ContentType = Literal[
    "product_description",
    "blog_post",
    "marketplace_listing",
    "category_page",
    "product_faq",
    "meta_tags",
    "full_campaign",
]

Platform = Literal["shopify", "amazon", "ebay", "etsy", "general"]
Tone = Literal["professional", "friendly", "persuasive", "luxury", "playful"]


class EcommerceGenerateRequest(BaseModel):
    product_name: str
    product_category: str = "General"
    key_features: str = ""
    pain_points: str = ""
    target_audience: str = "online shoppers"
    platform: Platform = "general"
    content_type: ContentType = "product_description"
    tone: Tone = "professional"


class EcommerceGenerateResponse(BaseModel):
    title: str
    meta_title: str
    meta_description: str
    focus_keyword: str
    secondary_keywords: list
    body: str
    faq: list
    schema_type: str
    seo_score: int
    ab_test_titles: Optional[list] = None
    social_captions: Optional[list] = None
    schema_json_ld: Optional[str] = None
    # Optional fields for marketplace listings
    bullet_points: Optional[list] = None
    # Optional OG/Twitter for meta_tags content type
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None


# ─────────────────────────────────────────────────────────────
# Endpoint
# ─────────────────────────────────────────────────────────────

@router.post("/generate", response_model=EcommerceGenerateResponse)
async def generate_ecommerce(
    body: EcommerceGenerateRequest,
    user=Depends(verify_supabase_token),
):
    """
    Generate SEO-optimized ecommerce content.
    Returns structured output: title, meta tags, keywords, body, FAQ, SEO score.
    """
    if not body.product_name.strip():
        raise HTTPException(status_code=422, detail="product_name is required.")

    try:
        result = await generate_ecommerce_content(
            product_name=body.product_name,
            product_category=body.product_category,
            key_features=body.key_features,
            pain_points=body.pain_points,
            target_audience=body.target_audience,
            platform=body.platform,
            content_type=body.content_type,
            tone=body.tone,
        )
    except Exception as e:
        print(f"[ECOMMERCE ROUTE ERROR] {e}")
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

    seo_score = calculate_seo_score(result)
    result["seo_score"] = seo_score

    # Ensure required fields with safe defaults
    result.setdefault("schema_type", "Product")
    result.setdefault("faq", [])
    result.setdefault("secondary_keywords", [])
    result.setdefault("ab_test_titles", None)
    result.setdefault("social_captions", None)
    result.setdefault("schema_json_ld", None)
    result.setdefault("bullet_points", None)
    result.setdefault("og_title", None)
    result.setdefault("og_description", None)
    result.setdefault("twitter_title", None)
    result.setdefault("twitter_description", None)

    return result


@router.get("/templates")
def get_ecommerce_templates():
    """Return available ecommerce content types with metadata."""
    return [
        {
            "id": "product_description",
            "label": "Product Description",
            "description": "SEO-optimized product copy for Shopify, WooCommerce & Google Shopping",
            "icon": "📦",
            "credit_cost": 5,
            "platforms": ["shopify", "general"],
        },
        {
            "id": "blog_post",
            "label": "Ecommerce Blog Post",
            "description": "Keyword-targeted blog posts that drive organic traffic to your store",
            "icon": "✍️",
            "credit_cost": 5,
            "platforms": ["shopify", "general"],
        },
        {
            "id": "marketplace_listing",
            "label": "Marketplace Listing",
            "description": "Amazon / eBay / Etsy listing with optimized title, bullets & description",
            "icon": "🛒",
            "credit_cost": 6,
            "platforms": ["amazon", "ebay", "etsy"],
        },
        {
            "id": "category_page",
            "label": "Category Page",
            "description": "SEO collection/category page descriptions for your store",
            "icon": "📚",
            "credit_cost": 4,
            "platforms": ["shopify", "general"],
        },
        {
            "id": "product_faq",
            "label": "Product FAQ",
            "description": "Structured FAQ for featured snippets and buyer confidence",
            "icon": "❓",
            "credit_cost": 3,
            "platforms": ["shopify", "amazon", "general"],
        },
        {
            "id": "meta_tags",
            "label": "Meta Tags Generator",
            "description": "Title, meta description, Open Graph & Twitter Card tags",
            "icon": "🏷️",
            "credit_cost": 2,
            "platforms": ["shopify", "general"],
        },
        {
            "id": "full_campaign",
            "label": "Full Campaign",
            "description": "All-in-one generator: description, social media captions, and ad copy aligned to your brand voice",
            "icon": "🚀",
            "credit_cost": 10,
            "platforms": ["shopify", "general", "amazon"],
        },
    ]
