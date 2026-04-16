"""
deduplication_service.py

Ensures unique content generation by:
1. Creating fingerprints of prompts and generated content
2. Tracking generation history to prevent duplicates
3. Enforcing variation when same prompt is requested multiple times
4. Storing content hashes to detect accidental duplication
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import httpx

from app.config import settings


class ContentDeduplicator:
    """
    Manages content uniqueness and prevents duplicate generation.
    """

    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.generation_history: Dict[str, list] = {}
        self.base_url = settings.XAI_API_BASE or "https://api.x.ai/v1"
        self.api_key = settings.XAI_API_KEY

    def _hash_content(self, content: str, method: str = "sha256") -> str:
        """Create a hash fingerprint of content for deduplication."""
        content_bytes = content.encode("utf-8")
        if method == "sha256":
            return hashlib.sha256(content_bytes).hexdigest()
        elif method == "md5":
            return hashlib.md5(content_bytes).hexdigest()
        return hashlib.sha1(content_bytes).hexdigest()

    def _hash_prompt(self, user_id: str, prompt: str, template: str = "") -> str:
        """Create a unique identifier for a prompt."""
        combined = f"{user_id}:{prompt}:{template}"
        return self._hash_content(combined)

    async def is_duplicate(
        self,
        content: str,
        user_id: str,
        threshold_hours: int = 24,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if content is duplicate or too similar to recent generation.
        Returns (is_duplicate, reason)
        """
        content_hash = self._hash_content(content)

        # Check exact match in cache
        if user_id in self.generation_history:
            for history_entry in self.generation_history[user_id]:
                if history_entry.get("content_hash") == content_hash:
                    time_diff = datetime.now() - datetime.fromisoformat(
                        history_entry["timestamp"]
                    )
                    if time_diff < timedelta(hours=threshold_hours):
                        return True, f"Exact duplicate from {time_diff.total_seconds() / 3600:.1f} hours ago"

        return False, None

    def track_generation(
        self,
        user_id: str,
        prompt: str,
        template: str,
        content: str,
        content_type: str = "text",
    ) -> Dict:
        """
        Record a generation event for future deduplication checks.
        """
        content_hash = self._hash_content(content)
        prompt_hash = self._hash_prompt(user_id, prompt, template)

        tracking_record = {
            "timestamp": datetime.now().isoformat(),
            "prompt_hash": prompt_hash,
            "content_hash": content_hash,
            "template": template,
            "content_type": content_type,
            "content_length": len(content),
            "prompt_preview": prompt[:100],
        }

        if user_id not in self.generation_history:
            self.generation_history[user_id] = []

        self.generation_history[user_id].append(tracking_record)

        # Keep only last 100 generations per user
        if len(self.generation_history[user_id]) > 100:
            self.generation_history[user_id] = self.generation_history[user_id][-100:]

        return tracking_record

    def get_variations_required(
        self,
        user_id: str,
        prompt: str,
        template: str,
        time_window_hours: int = 72,
    ) -> int:
        """
        Return how many times this prompt has been generated recently.
        Useful for deciding temperature adjustment.
        """
        prompt_hash = self._hash_prompt(user_id, prompt, template)
        count = 0

        if user_id in self.generation_history:
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            for entry in self.generation_history[user_id]:
                if entry["prompt_hash"] == prompt_hash:
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    if entry_time > cutoff_time:
                        count += 1

        return count


class UniquenessEnhancer:
    """
    Enhances prompts and post-processes content to ensure variety.
    """

    def __init__(self):
        self.variation_instructions = [
            "Create a completely different version with fresh perspectives and unique angles.",
            "Generate this with maximum creativity and originality—avoid any similarity to previous versions.",
            "Write this with novel structure, unexpected metaphors, and complete originality.",
            "Produce a radically different take—use alternative vocabulary, tone, and formatting.",
            "Create with utmost uniqueness—introduce surprising elements, new comparisons, and fresh insights.",
            "Generate with complete originality—vary the approach, tone, structure, and examples significantly.",
            "Produce a distinctly different version—change perspective, add unexpected dimensions.",
        ]

    def augment_prompt(self, prompt: str, variation_count: int = 0) -> str:
        """
        Augment prompt with uniqueness instructions based on variation count.
        Higher variation_count = more aggressive uniqueness requirement.
        """
        if variation_count == 0:
            return prompt

        variation_instruction = self.variation_instructions[
            min(variation_count, len(self.variation_instructions) - 1)
        ]

        return f"""{prompt}

UNIQUENESS REQUIREMENT [VARIATION #{variation_count + 1}]:
{variation_instruction}
Ensure this version is substantially different from any previous generation for this topic."""

    def adjust_temperature(self, base_temp: float, variation_count: int) -> float:
        """
        Adjust temperature dynamically based on variation count.
        More variations = higher temperature for more diversity.
        """
        # Start with base temperature, increase by 0.1 for each variation
        adjusted = base_temp + (variation_count * 0.08)
        # Cap at 0.95 (max safe temperature)
        return min(adjusted, 0.95)

    def post_process_for_uniqueness(
        self, content: str, content_type: str = "text"
    ) -> str:
        """
        Post-process generated content to enhance uniqueness.
        Applies synonym replacement and minor restructuring.
        """
        if content_type == "json":
            return content  # Don't modify JSON responses

        # Simple synonym mapping for common words (can be expanded)
        synonyms = {
            r"\binnovative\b": "groundbreaking",
            r"\brobust\b": "powerful",
            r"\beffective\b": "impactful",
            r"\brapid\b": "swift",
            r"\bsimple\b": "straightforward",
            r"\bcomplex\b": "multifaceted",
            r"\badvanced\b": "sophisticated",
            r"\bquick\b": "instantaneous",
            r"\bpowerful\b": "formidable",
            r"\bincredible\b": "remarkable",
        }

        import re

        processed = content
        for pattern, replacement in synonyms.items():
            # Only replace if not already the target word (to avoid re-replacement)
            processed = re.sub(
                pattern,
                lambda m: replacement if m.group(0).lower() != replacement.lower() else m.group(0),
                processed,
                flags=re.IGNORECASE,
            )

        return processed

    def add_uniqueness_markers(self, content: str) -> Dict:
        """
        Add markers indicating this content is unique/distinct.
        Useful for frontend UI and tracking.
        """
        return {
            "content": content,
            "uniqueness_score": self._calculate_uniqueness_score(content),
            "generated_at": datetime.now().isoformat(),
            "is_unique": True,
        }

    def _calculate_uniqueness_score(self, content: str) -> float:
        """
        Simple metric for uniqueness (0-100).
        Based on vocabulary diversity and structure.
        """
        words = content.lower().split()
        unique_words = set(words)

        # Calculate type-token ratio (vocabulary diversity)
        ttr = len(unique_words) / len(words) if words else 0

        # Calculate sentence variation
        sentences = [s.strip() for s in content.split(".") if s.strip()]
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(
            sentences
        ) if sentences else 0

        # Uniqueness score based on diversity and complexity
        diversity_score = min(ttr * 100, 100)  # TTR typically 0.4-0.6
        complexity_score = min(avg_sentence_length * 10, 40)  # 8-15 words = good

        uniqueness_score = (diversity_score * 0.6) + (complexity_score * 0.4)
        return round(uniqueness_score, 2)


# Create global instances
deduplicator = ContentDeduplicator()
uniqueness_enhancer = UniquenessEnhancer()
