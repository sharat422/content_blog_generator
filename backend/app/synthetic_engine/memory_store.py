# app/synthetic_engine/memory_store.py
# Synthetic Twin Memory Engine (Supabase-backed)

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from app.services.supabase_service import supabase

TABLE_NAME = "twin_memories"

# Decay rules (in days)
LOW_IMPORTANCE_DAYS = 7
MEDIUM_IMPORTANCE_DAYS = 30
HIGH_IMPORTANCE_DAYS = 9999  # effectively no decay for high-importance

# Max memories to send to LLM
MAX_RELEVANT_MEMORIES = 8


# ------------------------------------------------------
# Time helpers
# ------------------------------------------------------
def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_tz(dt) -> datetime:
    """
    Normalize timestamps coming back from Supabase:
    - They might be naive datetime, aware datetime, or ISO strings.
    """
    if dt is None:
        return _utc_now()

    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    if isinstance(dt, str):
        s = dt.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(s)
        except ValueError:
            return _utc_now()
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed

    # Fallback
    return _utc_now()


# ------------------------------------------------------
# Row <-> Memory mapping
# ------------------------------------------------------
def _row_to_memory(row: dict) -> dict:
    """
    Normalize DB row into in-app memory shape expected by SynthCore:

    {
        "id": ...,
        "user_id": ...,
        "role": "user" | "twin",
        "content": "text",
        "memory_type": "stm" | "ltm" | "goal" | "preference" | ...,
        "importance": float,
        "created_at": datetime,
        "last_used_at": datetime,
        "uses": int,
    }
    """
    return {
        "id": row.get("id"),
        "user_id": row.get("user_id"),
        "role": row.get("role") or row.get("speaker") or "user",
        "content": row.get("content") or row.get("memory_text") or "",
        "memory_type": row.get("memory_type") or "stm",
        "importance": float(row.get("importance") or 0.0),
        "created_at": ensure_tz(row.get("created_at")),
        "last_used_at": ensure_tz(row.get("last_used_at") or row.get("created_at")),
        "uses": int(row.get("uses") or 0),
    }


def _memory_to_row(mem: dict) -> dict:
    """
    Map in-app memory shape back to DB columns.
    We keep `memory_text` for backward compatibility with existing table.
    """
    return {
        "user_id": mem["user_id"],
        "role": mem.get("role", "user"),
        "memory_text": mem.get("content", ""),
        "memory_type": mem.get("memory_type", "stm"),
        "importance": mem.get("importance", 0.0),
        "created_at": mem.get("created_at", _utc_now()).isoformat(),
        "last_used_at": mem.get("last_used_at", _utc_now()).isoformat(),
        "uses": mem.get("uses", 0),
    }


# ------------------------------------------------------
# Core DB helpers
# ------------------------------------------------------
def _fetch_memories(user_id: str) -> List[dict]:
    """
    Fetch all memories for a user from Supabase, newest first.
    """
    if supabase is None:
        print("[MEMORY] Supabase client not configured – no memories loaded.")
        return []

    try:
        resp = (
            supabase.table(TABLE_NAME)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        rows = resp.data or []
        return [_row_to_memory(r) for r in rows]
    except Exception as e:
        #print(f"[MEMORY] Error fetching memories from Supabase: {e}")
        return []


def _insert_memory(mem: dict) -> Optional[dict]:
    if supabase is None:
        print("[MEMORY] Supabase client not configured – cannot persist memory.")
        return None

    row = _memory_to_row(mem)

    try:
        resp = supabase.table(TABLE_NAME).insert(row).execute()
        data = (resp.data or [row])[0]
        return _row_to_memory(data)
    except Exception as e:
        print(f"[MEMORY] Error inserting memory into Supabase: {e}")
        return None


def _update_memory_fields(mem_id, fields: dict):
    if supabase is None or mem_id is None:
        return
    try:
        supabase.table(TABLE_NAME).update(fields).eq("id", mem_id).execute()
    except Exception as e:
        print("[MEMORY] Error updating memory ")


def _delete_memories_by_ids(ids: List):
    if supabase is None or not ids:
        return
    try:
        supabase.table(TABLE_NAME).delete().in_("id", ids).execute()
    except Exception as e:
        print("[MEMORY] Error deleting memories")


# ------------------------------------------------------
# PUBLIC API – used by SynthCore
# ------------------------------------------------------
def add_memory(
    user_id: str,
    role: str = "user",
    content: str = "",
    memory_type: str = "stm",
    importance: float = 0.0,
):
    """
    Store a new memory row in Supabase.
    This signature matches how SynthCore calls add_memory().
    """
    mem = {
        "user_id": user_id,
        "role": role,
        "content": content,
        "memory_type": memory_type,
        "importance": importance,
        "created_at": _utc_now(),
        "last_used_at": _utc_now(),
        "uses": 0,
    }

    stored = _insert_memory(mem)
    preview = content[:60].replace("\n", " ")
    #print(f"🧠 [MEMORY ADDED] {memory_type} ({importance:.2f}) | {preview}...")
    return stored or mem


def decay_memory(user_id: str):
    """
    Apply decay rules directly in Supabase by deleting old, low-value memories.
    High-importance memories are preserved.
    """
    memories = _fetch_memories(user_id)
    if not memories:
        return

    now = _utc_now()
    ids_to_delete: List = []

    for m in memories:
        created_at = m["created_at"]
        importance = m.get("importance", 0.0)
        age_days = (now - created_at).days

        # High importance – keep effectively forever
        if importance >= 0.7:
            continue

        # Medium importance decay
        if 0.3 <= importance < 0.7:
            if age_days >= MEDIUM_IMPORTANCE_DAYS:
                ids_to_delete.append(m["id"])
            continue

        # Low importance decay
        if importance < 0.3:
            if age_days >= LOW_IMPORTANCE_DAYS:
                ids_to_delete.append(m["id"])
            continue

    if ids_to_delete:
        #print(f"🧹 [MEMORY DECAY] Deleting {len(ids_to_delete)} memories for {user_id}")
        _delete_memories_by_ids(ids_to_delete)


def _score_memory(m: dict, query: str = "") -> float:
    """
    Scoring used by get_relevant_memories:
    - importance
    - recency
    - usage
    - simple text match
    """
    score = 0.0

    # Importance (0–1) -> 0–5 pts
    score += m.get("importance", 0.0) * 5.0

    # Recency boost (last 24h gets extra weight)
    last_used = ensure_tz(m.get("last_used_at") or m.get("created_at"))
    hours = (_utc_now() - last_used).total_seconds() / 3600.0
    score += max(0.0, 24.0 - hours) / 24.0

    # Usage frequency
    score += m.get("uses", 0) * 0.3

    # Simple relevance match
    if query and query.lower() in m.get("content", "").lower():
        score += 3.0

    return score


def get_relevant_memories(
    user_id: str,
    query: str = "",
    limit: int = MAX_RELEVANT_MEMORIES,
) -> List[dict]:
    """
    Main retrieval function (not yet used by SynthCore, but ready).
    """
    memories = _fetch_memories(user_id)
    if not memories:
        return []

    scored = [( _score_memory(m, query), m ) for m in memories]
    scored.sort(key=lambda x: x[0], reverse=True)

    top = [m for _, m in scored[:limit]]

    # Mark as used in DB
    now_iso = _utc_now().isoformat()
    for m in top:
        new_uses = m.get("uses", 0) + 1
        _update_memory_fields(m["id"], {"uses": new_uses, "last_used_at": now_iso})
        m["uses"] = new_uses
        m["last_used_at"] = ensure_tz(now_iso)

    #print(f"📚 [MEMORY RETRIEVED] Returned {len(top)} memories for user {user_id}")
    return top


def get_recent_memory(user_id: str, limit: int = 12) -> List[dict]:
    """
    Compatibility API expected by SynthCore.
    Returns the most recent memories, newest first.
    """
    memories = _fetch_memories(user_id)
    memories.sort(key=lambda m: m["created_at"], reverse=True)
    return memories[:limit]


def get_important_memory(
    user_id: str,
    threshold: float = 0.6,
    limit: int = 40,
) -> List[dict]:
    """
    Compatibility API expected by SynthCore.
    Returns high-importance memories (LTM-like).
    """
    memories = _fetch_memories(user_id)
    important = [
        m for m in memories
        if float(m.get("importance") or 0.0) >= threshold
    ]

    important.sort(
        key=lambda m: (
            float(m.get("importance") or 0.0),
            ensure_tz(m.get("last_used_at") or m.get("created_at")),
        ),
        reverse=True,
    )
    return important[:limit]


def get_all_memories(user_id: str) -> List[dict]:
    """
    Debug / UI helper – returns all normalized memories for a user.
    """
    return _fetch_memories(user_id)
