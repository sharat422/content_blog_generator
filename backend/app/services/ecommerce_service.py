"""
ecommerce_service.py

Specialized SEO prompt engine for ecommerce sellers.
Returns structured content: title, meta tags, body, keywords, FAQ.
"""

import json
import httpx
from app.config import settings


# ─────────────────────────────────────────────────────────────
# SEO Prompt Templates (per content type)
# ─────────────────────────────────────────────────────────────

def _build_system_prompt(content_type: str) -> str:
    base = (
        "You are an expert ecommerce SEO copywriter with 10+ years of experience "
        "writing content that ranks on Google, converts shoppers, and follows "
        "Amazon/Shopify/eBay best practices. "
        "Always respond with a valid JSON object — no markdown, no code fences, just raw JSON."
    )

    instructions = {
        "product_description": (
            "Write an SEO-optimized product description. The JSON must have these keys:\n"
            "- title: H1-ready product title (include primary keyword naturally, 60-80 chars)\n"
            "- meta_title: SEO meta title, 50-60 chars, include brand/keyword\n"
            "- meta_description: Compelling 150-160 char meta description with CTA\n"
            "- focus_keyword: single primary keyword phrase\n"
            "- secondary_keywords: list of 5-8 LSI/related keywords as a JSON array\n"
            "- body: Full product description (200-400 words), uses H2 subheadings, "
            "bullet points for features, persuasive benefit-driven language, "
            "naturally includes focus keyword and secondary keywords\n"
            "- faq: list of 3 objects with 'question' and 'answer' keys each (structured data ready)\n"
            "- schema_type: always 'Product'"
        ),
        "blog_post": (
            "Write a full SEO blog post for ecommerce. The JSON must have these keys:\n"
            "- title: Engaging H1 blog title with primary keyword (under 70 chars)\n"
            "- meta_title: SEO meta title, 50-60 chars\n"
            "- meta_description: 150-160 char meta description, includes keyword and CTA\n"
            "- focus_keyword: single primary long-tail keyword\n"
            "- secondary_keywords: list of 6-10 related keywords as a JSON array\n"
            "- body: Full blog post body (600-900 words), uses H2/H3 subheadings, "
            "internal linking suggestions in [brackets], naturally integrates keywords, "
            "includes an intro hook, numbered tips or steps, and a CTA conclusion\n"
            "- faq: list of 4 objects with 'question' and 'answer' keys for FAQ schema\n"
            "- schema_type: always 'BlogPosting'"
        ),
        "marketplace_listing": (
            "Write a marketplace listing (Amazon/eBay/Etsy style). The JSON must have these keys:\n"
            "- title: Keyword-rich listing title (150-200 chars for Amazon, 80 chars for eBay)\n"
            "- meta_title: Short search-engine title (60 chars)\n"
            "- meta_description: 155-char description for Google Shopping snippet\n"
            "- focus_keyword: primary search keyword shoppers use\n"
            "- secondary_keywords: list of 8-10 backend/hidden keywords as JSON array\n"
            "- bullet_points: list of exactly 5 feature bullets, each starting with uppercase "
            "benefit word, under 200 chars each — as a JSON array\n"
            "- body: long product description (250-400 words) with keyword integration\n"
            "- faq: list of 3 Q&A objects that address common buyer objections\n"
            "- schema_type: always 'Product'"
        ),
        "category_page": (
            "Write SEO category/collection page content. The JSON must have these keys:\n"
            "- title: H1 category title with keyword\n"
            "- meta_title: 50-60 char meta title\n"
            "- meta_description: 150-160 char meta description with keyword\n"
            "- focus_keyword: category-level keyword (e.g., 'wireless headphones')\n"
            "- secondary_keywords: list of 6-8 sub-category or filter keywords as JSON array\n"
            "- body: Category page intro (150-300 words) — buyer-intent language, "
            "explains what products are in this category, includes keyword naturally\n"
            "- faq: list of 2-3 category FAQs as JSON objects with question/answer\n"
            "- schema_type: always 'CollectionPage'"
        ),
        "product_faq": (
            "Write a product FAQ optimized for Google Featured Snippets. The JSON must have these keys:\n"
            "- title: 'Frequently Asked Questions About [Product]' style H2 heading\n"
            "- meta_title: 55-char meta title for the FAQ page\n"
            "- meta_description: 155-char description mentioning the product and FAQs\n"
            "- focus_keyword: primary product keyword\n"
            "- secondary_keywords: list of 5-7 question-based keywords as JSON array\n"
            "- faq: list of 8 detailed Q&A objects with 'question' and 'answer' keys. "
            "Answers should be 40-80 words each, factual and direct\n"
            "- body: short intro paragraph (50-80 words) before the FAQs\n"
            "- schema_type: always 'FAQPage'"
        ),
        "meta_tags": (
            "Generate optimized meta tags for any ecommerce page. The JSON must have these keys:\n"
            "- title: Page heading suggestion\n"
            "- meta_title: Exactly 50-60 chars, compelling and keyword-rich\n"
            "- meta_description: Exactly 150-160 chars with keyword and action CTA\n"
            "- focus_keyword: single primary keyword\n"
            "- secondary_keywords: list of 5 alternative/related keyword phrases as JSON array\n"
            "- og_title: Open Graph title for social sharing (under 95 chars)\n"
            "- og_description: Open Graph description for social sharing (under 200 chars)\n"
            "- twitter_title: Twitter Card title (under 70 chars)\n"
            "- twitter_description: Twitter Card description (under 200 chars)\n"
            "- body: brief notes on keyword strategy (100-150 words)\n"
            "- faq: empty list []\n"
            "- schema_type: 'WebPage'"
        ),
    }

    return base + "\n\n" + instructions.get(content_type, instructions["product_description"])


def _build_user_prompt(
    product_name: str,
    product_category: str,
    key_features: str,
    target_audience: str,
    platform: str,
    content_type: str,
    tone: str,
) -> str:
    platform_map = {
        "shopify": "Shopify / WooCommerce store",
        "amazon": "Amazon marketplace",
        "ebay": "eBay marketplace",
        "etsy": "Etsy marketplace",
        "general": "general ecommerce / Google Shopping",
    }

    tone_map = {
        "professional": "professional and authoritative",
        "friendly": "friendly and approachable",
        "persuasive": "urgency-driven and highly persuasive",
        "luxury": "premium and aspirational",
        "playful": "fun and energetic",
    }

    return (
        f"Product / Page: {product_name}\n"
        f"Category: {product_category}\n"
        f"Key Features / Details: {key_features}\n"
        f"Target Audience: {target_audience}\n"
        f"Platform: {platform_map.get(platform, platform)}\n"
        f"Content Type: {content_type.replace('_', ' ').title()}\n"
        f"Tone: {tone_map.get(tone, tone)}\n\n"
        "Generate the content now. Return ONLY the JSON object."
    )


# ─────────────────────────────────────────────────────────────
# Core Generation Function
# ─────────────────────────────────────────────────────────────

async def generate_ecommerce_content(
    product_name: str,
    product_category: str,
    key_features: str,
    target_audience: str,
    platform: str,
    content_type: str,
    tone: str,
) -> dict:
    """
    Call the LLM with an ecommerce-specific SEO prompt and return a
    structured dictionary with title, meta tags, body, keywords, and FAQ.
    """

    system_prompt = _build_system_prompt(content_type)
    user_prompt = _build_user_prompt(
        product_name=product_name,
        product_category=product_category,
        key_features=key_features,
        target_audience=target_audience,
        platform=platform,
        content_type=content_type,
        tone=tone,
    )

    payload = {
        "model": settings.model_name,
        "temperature": 0.65,  # slightly lower for more factual/structured output
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    headers = {
        "Authorization": f"Bearer {settings.XAI_API_KEY}",
        "Content-Type": "application/json",
    }

    print(f"\n[ECOMMERCE] Generating '{content_type}' for '{product_name}' on {platform}")

    try:
        async with httpx.AsyncClient(base_url=settings.XAI_API_BASE, timeout=120.0) as client:
            response = await client.post("/chat/completions", json=payload, headers=headers)
    except httpx.RequestError as e:
        raise Exception(f"Network error calling LLM: {e}")

    if response.status_code != 200:
        print(f"[ECOMMERCE ERROR] {response.status_code}: {response.text}")
        raise Exception(f"LLM API error {response.status_code}: {response.text}")

    data = response.json()
    raw_text = data["choices"][0]["message"]["content"].strip()

    # Strip any accidental markdown fences the model might add
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"[ECOMMERCE] JSON parse failed: {e}\nRaw: {raw_text[:500]}")
        # Graceful fallback: return raw text in body field
        result = {
            "title": product_name,
            "meta_title": product_name[:60],
            "meta_description": f"Shop {product_name} - {product_category}",
            "focus_keyword": product_name.lower(),
            "secondary_keywords": [],
            "body": raw_text,
            "faq": [],
            "schema_type": "Product",
        }

    print(f"[ECOMMERCE] SUCCESS — keys returned: {list(result.keys())}")
    return result


# ─────────────────────────────────────────────────────────────
# SEO Score Calculator (used by API response)
# ─────────────────────────────────────────────────────────────

def calculate_seo_score(result: dict) -> int:
    """
    Simple heuristic SEO score (0-100) based on structured output quality.
    """
    score = 0
    checks = [
        # Meta title: exists and within 50-60 chars
        (bool(result.get("meta_title")) and 50 <= len(result.get("meta_title", "")) <= 65, 20),
        # Meta description: exists and within 130-165 chars
        (bool(result.get("meta_description")) and 130 <= len(result.get("meta_description", "")) <= 165, 20),
        # Focus keyword present
        (bool(result.get("focus_keyword")), 10),
        # Secondary keywords: at least 3
        (isinstance(result.get("secondary_keywords"), list) and len(result.get("secondary_keywords", [])) >= 3, 10),
        # Body: at least 150 words
        (len(result.get("body", "").split()) >= 150, 20),
        # Title: present
        (bool(result.get("title")), 10),
        # FAQ: at least 2 entries
        (isinstance(result.get("faq"), list) and len(result.get("faq", [])) >= 2, 10),
    ]
    for condition, points in checks:
        if condition:
            score += points
    return score
