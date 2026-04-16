import os
import json
import httpx
import jwt
import asyncio
import time

JWT_SECRET = "eMbfxShfSdCSpazih6yAexf4tXohPkP7etPtoAtTU0n0ey5r1feKdOnFmazuJYqFSkAYQWo/DojOg8vc1dhqzQ=="

def create_mock_jwt():
    payload = {
        "sub": "test_user_123",
        "email": "test@example.com",
        "aud": "authenticated",
        "role": "authenticated",
        "exp": int(time.time()) + 3600
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

async def test_generate():
    token = create_mock_jwt()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "product_name": "Test Wireless Headphones",
        "product_category": "Electronics",
        "key_features": "Noise cancelling, Bluetooth 5.0",
        "target_audience": "Music lovers",
        "platform": "shopify",
        "content_type": "product_description",
        "tone": "professional"
    }
    
    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0) as client:
        response = await client.post("/api/ecommerce/generate", json=payload, headers=headers)
        print("Status code:", response.status_code)
        try:
            print("Response:", json.dumps(response.json(), indent=2))
        except Exception as e:
            print("Failed to decode JSON:", response.text)

if __name__ == "__main__":
    asyncio.run(test_generate())
