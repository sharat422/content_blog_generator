import asyncio
from app.services.ecommerce_service import generate_ecommerce_content
from app.api.ecommerce import calculate_seo_score
import json

async def run_test():
    print("Beginning test for product_description...")
    result = await generate_ecommerce_content(
        product_name="Sony WH-1000XM5",
        product_category="Electronics",
        key_features="Industry-leading noise cancellation, 30-hour battery life",
        pain_points="Crying babies on airplanes, uncomfortable tight fit for long sessions",
        target_audience="Frequent flyers and audiophiles",
        platform="shopify",
        content_type="full_campaign",
        tone="professional"
    )
    
    print("\n\n=== RESULT JSON ===")
    print(json.dumps(result, indent=2))
    
    score = calculate_seo_score(result)
    print("\nCalculated SEO Score:", score)

if __name__ == "__main__":
    asyncio.run(run_test())
