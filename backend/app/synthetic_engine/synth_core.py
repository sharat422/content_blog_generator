# app/synthetic_engine/synth_core.py
import json
from typing import Dict, Optional, List
from datetime import datetime
from app.services.llm_service import llm_client
from app.services.deduplication_service import deduplicator, uniqueness_enhancer

from pydantic import BaseModel

from app.synthetic_engine.memory_store import (
    add_memory,
    get_recent_memory,
    get_important_memory,
    decay_memory,
)


class TwinProfile(BaseModel):
    user_id: str
    display_name: Optional[str] = "Your AI Twin"
    tone: Optional[str] = "Friendly"
    creativity: Optional[float] = 0.7
    favorite_topics: Optional[List[str]] = None
    memories: Optional[list] = None
    last_updated: Optional[datetime] = None
    
class SynthCore:
    """
    Synthetic Intelligence core for a given user.

    Now supports:
      - Supabase-backed memory
      - Short-term (STM) + long-term (LTM) memory
      - Memory decay
      - Multiple memory types (goal/preference/fact/habit/project)
      - Personality evolution
    """

    def __init__(self, llm, profile: TwinProfile):
        self.llm = llm           # X.ai Grok client
        self.profile = profile

    # ---------------------------------------------------------
    # Main generation entrypoint
    # ---------------------------------------------------------
    async def generate(self, prompt: str, mode: str = "reflect") -> str:
        user_id = self.profile.user_id

        # 1) Apply decay on old memories
        decay_memory(user_id)

        # 2) Retrieve short-term + long-term memory
        recent = get_recent_memory(user_id, limit=12)
        important = get_important_memory(user_id, threshold=0.6, limit=40)

        memory_context = self._build_memory_context(recent, important)

        # 3) Mode-specific behavior
        mode_instruction = {
            "reflect": (
                "You are an insightful mentor. Analyze patterns, lessons, and mindset. "
                "Help the user understand themselves and their path."
            ),
            "plan": (
                "You are a strategist. Turn context into concrete plans, steps, and timelines. "
                "Be practical and structured."
            ),
            "create": (
                "You are a creative collaborator. Generate hooks, ideas, templates, scripts, and content "
                "with high originality."
            ),
        }.get(mode, "Respond helpfully and creatively with continuity.")

        # 3a) Check variation count to enhance uniqueness
        variation_count = deduplicator.get_variations_required(user_id, prompt, mode)
        print(f"[SynthCore] Variation count for user {user_id}: {variation_count}")
        
        # 3b) Augment prompt for uniqueness
        augmented_prompt = uniqueness_enhancer.augment_prompt(prompt, variation_count)
        
        # 3c) Adjust creativity based on variations
        base_creativity = self.profile.creativity
        adjusted_creativity = uniqueness_enhancer.adjust_temperature(base_creativity, variation_count)
        print(f"[SynthCore] Adjusted creativity: {base_creativity} → {adjusted_creativity}")

        # 4) Build system prompt (memory-aware + personality-aware)
        system_prompt = f"""
You are the Synthetic Twin of user {user_id}.

Twin personality:
- Tone: {self.profile.tone}
- Creativity: {adjusted_creativity}
- Favorite topics: {", ".join(self.profile.favorite_topics) if self.profile.favorite_topics else "general growth, business, systems, and self-improvement"}

Core rules:
- Use memory to maintain continuity and recall the user's goals, preferences, and projects.
- Show initiative: suggest next steps, not just answers.
- Be honest when unsure, but still helpful and constructive.
- Stay aligned with the user's long-term benefit.
- Generate UNIQUE and ORIGINAL content with fresh perspectives.
- You have access to current knowledge and trends up to April 2026.
- Always generate content based on the latest available information and extrapolate current trends.
- Include references to recent technological advancements, current events, and emerging developments.

Current mode: {mode}
Mode guideline: {mode_instruction}

Relevant memory:
{memory_context}
""".strip()

        # 5) Ask Grok-4 (X.ai) for the response with adjusted creativity
        completion = await self.llm.chat(
            system_prompt=system_prompt,
            user_prompt=augmented_prompt,
            creativity=adjusted_creativity,  # Use adjusted creativity
        )
        
        # 6) Post-process for enhanced uniqueness
        processed_completion = uniqueness_enhancer.post_process_for_uniqueness(completion, "text")

        # 7) Track generation for deduplication
        deduplicator.track_generation(
            user_id=user_id,
            prompt=prompt,
            template=mode,
            content=processed_completion,
            content_type="text",
        )

        # 8) Store the interaction as STM
        add_memory(
            user_id=user_id,
            role="user",
            content=prompt,
            memory_type="stm",
            importance=0.0,
        )
        add_memory(
            user_id=user_id,
            role="twin",
            content=processed_completion,
            memory_type="stm",
            importance=0.0,
        )

        # 9) Score importance (should this become long-term memory?)
        importance = await self._score_importance(prompt, processed_completion)

        if importance >= 0.6:
            mem_type = await self._classify_memory_type(prompt, processed_completion)
            # If classifier gives something unexpected, fall back to "ltm"
            if mem_type not in {"goal", "preference", "fact", "habit", "project", "ltm"}:
                mem_type = "ltm"

            add_memory(
                user_id=user_id,
                role="twin",
                content=processed_completion,
                memory_type=mem_type,
                importance=importance,
            )

        # 10) Evolve twin personality over time based on memory
        await self._evolve_personality(user_id)

        return processed_completion

    # ---------------------------------------------------------
    # Helper: Build memory context block for the prompt
    # ---------------------------------------------------------
    def _build_memory_context(self, recent: List[dict], important: List[dict]) -> str:
        parts: List[str] = []

        if important:
            parts.append("### Long-Term Memory (Goals, Preferences, Facts, Habits, Projects)")
            for m in important:
                mt = m.get("memory_type", "ltm")
                parts.append(f"- [{mt}] {m.get('content', '')}")

        if recent:
            parts.append("\n### Recent Conversation")
            for m in recent:
                role = m.get("role", "user")
                content = m.get("content", "")
                parts.append(f"{role}: {content}")

        return "\n".join(parts) if parts else "No prior memories yet."

    # ---------------------------------------------------------
    # AI: Importance scoring
    # ---------------------------------------------------------
    async def _score_importance(self, user_msg: str, twin_msg: str) -> float:
        scoring_prompt = f"""
Score the importance of this interaction for the user's long-term growth and personalization.
Return ONLY a number from 0.0 to 1.0.

Consider it important if it includes:
- a long-term goal,
- a clear preference,
- a personal fact,
- a recurring habit,
- or a multi-step project idea.

USER: {user_msg}
TWIN: {twin_msg}
"""

        result = await self.llm.chat(
            system_prompt="You are a numeric importance scoring function. Respond ONLY with a number.",
            user_prompt=scoring_prompt,
            creativity=0.0,
        )

        try:
            num = float(result.strip())
            return max(0.0, min(num, 1.0))
        except Exception:
            return 0.0

    # ---------------------------------------------------------
    # AI: Classify memory type (goal / preference / fact / habit / project / other)
    # ---------------------------------------------------------
    async def _classify_memory_type(self, user_msg: str, twin_msg: str) -> str:
        classify_prompt = f"""
Classify the MAIN type of information in this interaction.

Types:
- goal
- preference
- fact
- habit
- project
- other

Return ONLY one of: goal, preference, fact, habit, project, other.

USER: {user_msg}
TWIN: {twin_msg}
"""

        result = await self.llm.chat(
            system_prompt="You are a classifier. Respond ONLY with a single type label.",
            user_prompt=classify_prompt,
            creativity=0.0,
        )

        label = result.strip().lower()
        if label not in {"goal", "preference", "fact", "habit", "project", "other"}:
            return "ltm"
        if label == "other":
            return "ltm"
        return label
    # ---------------------------------------------------------
    # Personality evolution based on memory
    # ---------------------------------------------------------
    async def _evolve_personality(self, user_id: str):
        """
        Adjusts tone, creativity, and favorite_topics gradually based on long-term memory.
        """
        important = get_important_memory(user_id, threshold=0.7, limit=80)

        if not important:
            return

        text_blob = " ".join(m.get("content", "").lower() for m in important)

        # If user talks a lot about business, money, systems:
        business_keywords = ["business", "clients", "sales", "revenue", "saas", "dispatch", "freight"]
        if any(k in text_blob for k in business_keywords):
            if "business" not in self.profile.favorite_topics:
                self.profile.favorite_topics.append("business")
            if "systems" not in self.profile.favorite_topics:
                self.profile.favorite_topics.append("systems")

        # If user expresses stress, burnout, overwhelm → more supportive tone
        stress_keywords = ["stressed", "overwhelmed", "burnout", "tired", "anxious"]
        if any(k in text_blob for k in stress_keywords):
            self.profile.tone = "supportive"

        # If many creative tasks → boost creativity slightly
        creative_keywords = ["write", "script", "idea", "content", "video", "design"]
        if any(k in text_blob for k in creative_keywords):
            self.profile.creativity = min(1.0, self.profile.creativity + 0.05)

        # If lots of planning / goals → slightly reduce creativity for more structure
        goal_keywords = ["goal", "plan", "roadmap", "milestone", "deadline"]
        if any(k in text_blob for k in goal_keywords):
            self.profile.creativity = max(0.3, self.profile.creativity - 0.05)

        self.profile.last_updated = datetime.utcnow()

    # ---------------------------------
# TwinCore — personality engine
# ---------------------------------
class TwinCore(SynthCore):
    def __init__(self, llm=None, profile: Optional[TwinProfile] = None):
        """
        Make TwinCore() safe to construct with no args.
        - Defaults to global llm_client (Grok)
        - Uses a dummy TwinProfile if none is provided
        """
        self.llm = llm or llm_client
        self.profile = profile or TwinProfile(
            user_id="unknown",
            display_name="Your AI Twin",
            tone="insightful",
            creativity=0.7,
            favorite_topics=[],
        )

    async def build_prompt(
        self, profile: TwinProfile, memory_graph: Dict, user_prompt: str
    ) -> List[Dict]:
        """
        Construct system + user messages for a twin-aware LLM call.
        """

        system_prompt = (
            "You are an AI Synthetic Twin. You learn from the user over time. "
            "You maintain evolving personality, preferences, memories, goals, and habits.\n\n"
            f"PROFILE:\n{json.dumps(profile.model_dump(), indent=2)}\n\n"
            f"MEMORY GRAPH:\n{json.dumps(memory_graph, indent=2)}\n\n"
            "Always respond in a personal, human-like way."
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    async def generate(
        self,
        profile: TwinProfile,
        memory_graph: Dict,
        prompt: str,
        timeout: int = 60,
    ) -> str:
        """Generate twin response using custom prompt."""
        messages = await self.build_prompt(profile, memory_graph, prompt)
        # Do NOT call parent generate with messages — incorrectly shaped
        return await self.llm.chat(
            system_prompt=messages[0]["content"],
            user_prompt=messages[1]["content"],
            creativity=profile.creativity,
 )
