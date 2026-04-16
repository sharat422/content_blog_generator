#!/usr/bin/env python3
"""
test_knowledge_update.py

Test script to verify that the knowledge update service is working
and content generation includes 2026 context.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.knowledge_update_service import knowledge_service
from app.services.llm_service import generate_llm_content


async def test_knowledge_service():
    """Test the knowledge update service functionality."""

    print("=== Knowledge Update Service Test ===\n")

    # Test 1: Check knowledge base initialization
    print("1. Knowledge Base Summary:")
    summary = knowledge_service.get_knowledge_summary()
    print(summary)

    # Test 2: Check current context prompt
    print("2. Current Context Prompt:")
    context = knowledge_service.get_current_context_prompt()
    print(context[:300] + "...\n")

    # Test 3: Test prompt enhancement
    print("3. Prompt Enhancement Test:")
    original = "Write a blog about AI technology"
    enhanced = knowledge_service.enhance_prompt_with_current_knowledge(original, "blog")
    print(f"Original: {original}")
    print(f"Enhanced length: {len(enhanced)} characters")
    print(f"Contains 2026: {'2026' in enhanced}")
    print(f"Contains trends: {'trends' in enhanced.lower()}\n")

    # Test 4: Test trend insights
    print("4. Trend Insights Test:")
    insights_prompt = knowledge_service.get_trend_insights("artificial intelligence")
    print(f"Insights prompt length: {len(insights_prompt)}")
    print(f"Contains current year: {'2026' in insights_prompt}\n")

    print("=== Knowledge Service Tests Complete ===")


async def test_content_generation():
    """Test that content generation includes current knowledge."""

    print("\n=== Content Generation Test ===\n")

    try:
        # Test blog generation with current knowledge
        prompt = "Write a blog post about the future of remote work"
        print(f"Testing content generation with prompt: '{prompt}'")

        # This will use the enhanced prompt with current knowledge
        content = await generate_llm_content(prompt, "Blog Post", user_id="test_user")

        print(f"Generated content length: {len(content)} characters")
        print(f"Contains 2026 reference: {'2026' in content}")
        print(f"Contains current trends: {any(trend in content.lower() for trend in ['ai', 'remote', 'technology', 'future'])}")

        # Show first 500 characters
        print(f"\nContent preview (first 500 chars):\n{content[:500]}...")

    except Exception as e:
        print(f"Error in content generation test: {e}")
        print("This might be due to missing API keys or network issues.")

    print("\n=== Content Generation Test Complete ===")


if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_knowledge_service())
    asyncio.run(test_content_generation())