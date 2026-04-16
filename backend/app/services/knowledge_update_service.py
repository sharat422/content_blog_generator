"""
knowledge_update_service.py

Service to keep AI content generation current with latest trends and information.
Provides mechanisms to update knowledge base and generate content with 2026 context.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from app.services.llm_service import llm_client
from app.config import settings


class KnowledgeUpdateService:
    """
    Service to maintain current knowledge and trends for content generation.
    """

    def __init__(self):
        self.current_year = 2026
        self.current_month = "April"
        self.knowledge_base = self._initialize_knowledge_base()

    def _initialize_knowledge_base(self) -> Dict:
        """Initialize with current trends and knowledge up to 2026."""
        return {
            "current_year": self.current_year,
            "current_month": self.current_month,
            "key_trends_2026": [
                "AI-powered personalization in ecommerce",
                "Sustainable and eco-friendly products",
                "Remote work optimization tools",
                "Mental health and wellness technology",
                "Cryptocurrency mainstream adoption",
                "Extended reality (XR) experiences",
                "Quantum computing applications",
                "Autonomous vehicle integration",
                "Climate tech innovations",
                "Personalized education platforms"
            ],
            "emerging_technologies": [
                "Advanced AI assistants with emotional intelligence",
                "Brain-computer interfaces",
                "Nanotechnology in consumer products",
                "Space tourism accessibility",
                "Advanced robotics in daily life",
                "Biometric security systems",
                "Smart city infrastructure",
                "Vertical farming technology",
                "Advanced renewable energy solutions",
                "Personalized medicine breakthroughs"
            ],
            "market_shifts": [
                "Shift from ownership to subscription models",
                "Rise of direct-to-consumer brands",
                "Increased focus on data privacy",
                "Growth of remote and hybrid work",
                "Expansion of gig economy platforms",
                "Integration of AI in customer service",
                "Focus on mental health in workplace",
                "Sustainable business practices",
                "Personalized marketing at scale",
                "Integration of Web3 technologies"
            ],
            "consumer_behavior_2026": [
                "Preference for sustainable products",
                "Demand for personalized experiences",
                "Increased digital literacy",
                "Focus on work-life balance",
                "Interest in lifelong learning",
                "Concern for data privacy",
                "Preference for ethical brands",
                "Interest in wellness products",
                "Demand for convenience solutions",
                "Focus on community and social impact"
            ]
        }

    def get_current_context_prompt(self) -> str:
        """Generate a prompt that provides current context for content generation."""
        trends = ", ".join(self.knowledge_base["key_trends_2026"][:5])
        technologies = ", ".join(self.knowledge_base["emerging_technologies"][:5])
        behaviors = ", ".join(self.knowledge_base["consumer_behavior_2026"][:5])

        return f"""
Current Context (as of {self.current_month} {self.current_year}):
- Key Trends: {trends}
- Emerging Technologies: {technologies}
- Consumer Behavior: {behaviors}

Generate content that reflects these current realities and extrapolates natural progressions of these trends.
"""

    def enhance_prompt_with_current_knowledge(self, original_prompt: str, content_type: str = "general") -> str:
        """Enhance any prompt with current knowledge and trends."""

        context_prompt = self.get_current_context_prompt()

        enhancement_instructions = {
            "blog": """
When writing blog content, consider:
- Current events and their impact on the topic
- Recent technological developments
- Evolving consumer preferences
- Future trends and predictions
- Real-world applications of emerging technologies
""",
            "product": """
When writing product content, consider:
- Current market demands and consumer needs
- Latest technological integrations
- Sustainability and ethical considerations
- Competitive landscape in 2026
- Future-proof features and benefits
""",
            "social": """
When writing social media content, consider:
- Current viral trends and formats
- Platform algorithms and best practices
- Audience engagement patterns in 2026
- Cultural and social movements
- Real-time relevance and timeliness
""",
            "general": """
Generate content that feels current and relevant to 2026 audiences.
"""
        }

        instruction = enhancement_instructions.get(content_type, enhancement_instructions["general"])

        return f"""{original_prompt}

{instruction}

{context_prompt}

Ensure all content reflects knowledge and trends current as of {self.current_month} {self.current_year}."""

    def get_trend_insights(self, topic: str) -> str:
        """Get trend insights for a specific topic."""
        base_prompt = f"Provide insights on {topic} trends and developments as of {self.current_month} {self.current_year}."

        return self.enhance_prompt_with_current_knowledge(base_prompt, "general")

    async def generate_current_content(self, topic: str, content_type: str = "blog") -> str:
        """Generate content with explicit current knowledge instructions."""

        enhanced_prompt = self.enhance_prompt_with_current_knowledge(
            f"Write a {content_type} about {topic}",
            content_type
        )

        # Use the LLM service to generate content
        from app.services.llm_service import generate_llm_content

        return await generate_llm_content(enhanced_prompt, content_type)

    def update_knowledge_base(self, new_trends: List[str], category: str = "key_trends_2026"):
        """Update the knowledge base with new trends."""
        if category in self.knowledge_base:
            self.knowledge_base[category].extend(new_trends)
            # Remove duplicates
            self.knowledge_base[category] = list(set(self.knowledge_base[category]))

    def get_knowledge_summary(self) -> str:
        """Get a summary of current knowledge for debugging."""
        return f"""
Knowledge Base Summary ({self.current_month} {self.current_year}):
- {len(self.knowledge_base['key_trends_2026'])} key trends tracked
- {len(self.knowledge_base['emerging_technologies'])} emerging technologies
- {len(self.knowledge_base['market_shifts'])} market shifts identified
- {len(self.knowledge_base['consumer_behavior_2026'])} consumer behavior patterns
"""


# Global instance
knowledge_service = KnowledgeUpdateService()
