# app/services/supabase_service.py

import os
import requests
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client


# ---------------------------------------------
# Load environment variables
# ---------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")  # New admin bypass variable

HEADERS = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}
# ---------------------------------------------
# Initialize Supabase client
# ---------------------------------------------
supabase: Client | None = None

if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        #print(f"[SUPABASE] Client initialized for {SUPABASE_URL}")
    except Exception as e:
        print(f"[SUPABASE] ERROR initializing Supabase client: {e}")
else:
    print("[SUPABASE] Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")


# ============================================================================
# MEMORY SYSTEM
# ============================================================================

def load_memories(user_id: str):
    """Load all memories for a user."""
    
    url = f"{SUPABASE_URL}/rest/v1/twin_memories?user_id=eq.{user_id}&select=*&order=created_at.asc"

    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        print("[ERROR] Error loading memories:", res.text)
        return []

    # Ensure timestamps are parsed safely
    memories = res.json()

    return memories


def save_memory(user_id: str, memory_text: str, memory_type: str):
    """Insert a new memory row into Supabase."""
    
    url = f"{SUPABASE_URL}/rest/v1/twin_memories"

    payload = {
        "user_id": user_id,
        "memory_text": memory_text,
        "memory_type": memory_type,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    res = requests.post(url, headers=HEADERS, json=payload)

    if res.status_code not in (200, 201):
        print("[ERROR] Error saving memory:", res.text)
# -------------------------------------------------
# EXISTING: plan + profile helpers
# -------------------------------------------------
def set_user_plan(
    user_id: str,
    plan: str,
    stripe_customer_id: str | None = None,
    stripe_subscription_id: str | None = None,
    subscription_status: str | None = None,
) -> None:
    """
    Upsert the user's plan & Stripe IDs into the `user_plans` table.
    """
    if supabase is None:
        print("[SUPABASE] set_user_plan called but client not configured")
        return

    data = {
        "user_id": user_id,
        "plan": plan,
        "stripe_customer_id": stripe_customer_id,
        "stripe_subscription_id": stripe_subscription_id,
        "subscription_status": subscription_status or "active",
    }

    print(f"[SUPABASE] Upserting user_plans row: {data}")

    try:
        supabase.table("user_plans").upsert(data).execute()
    except Exception as e:
        print(f"[SUPABASE] ERROR upserting user_plans: {e}")


def fetch_user_profile(user_id: str):
    """Fetch user profile from Supabase."""
    if supabase is None:
        return None
    try:
        resp = supabase.table("user_profiles").select("*").eq("user_id", user_id).maybe_single().execute()
        return resp.data
    except Exception as e:
        print(f"[SUPABASE] ERROR fetching user_profile: {e}")
        return None

def upsert_user_profile(user_id: str, bio: str, tone: str, goals: str):
    if supabase is None:
        return None
    profile = {
        "user_id": user_id,
        "bio": bio,
        "tone": tone,
        "goals": goals,
    }
    return supabase.table("user_profiles").upsert(profile).execute()

def save_user_profile(user_id: str, profile: dict):
    if supabase is None:
        return None
    profile["user_id"] = user_id
    return (
        supabase.table("user_profiles")
        .upsert(profile)
        .execute()
    )


# -------------------------------------------------
# NEW: credit-based usage system
# -------------------------------------------------
COST_IMAGE_GEN_BASIC = 25       # e.g., DALL-E 2 standard
COST_VIDEO_GEN_STANDARD = 500   # Video generation (includes planning, TTS, and multiple DALL-E calls)
FREE_INITIAL_CREDITS = 100       # one-time when user registers
PRO_MONTHLY_CREDITS = 6000       # refill on each paid billing cycle


def initialize_user_credits(user_id: str, initial_credits: int = FREE_INITIAL_CREDITS):
    """
    Give a new user their initial free credits.
    Call this once right after registration.
    """
    if supabase is None:
        print("[SUPABASE] initialize_user_credits called but client not configured")
        return

    now = datetime.utcnow()
    period_end = now + timedelta(days=30)

    print(
        f"[SUPABASE] Initializing credits for {user_id} "
        f"to {initial_credits}"
    )

    try:
        supabase.table("user_credits").upsert(
            {
                "user_id": user_id,
                "credits": initial_credits,
                "period_start": now.isoformat(),
                "period_end": period_end.isoformat(),
            }
        ).execute()
    except Exception as e:
        print(f"[SUPABASE] ERROR initializing user_credits: {e}")


def refill_pro_credits(user_id: str, amount: int = PRO_MONTHLY_CREDITS):
    """
    Set / refill credits for a Pro billing cycle.
    Call from Stripe webhook when invoice is paid or subscription is active.
    """
    if supabase is None:
        print("[SUPABASE] refill_pro_credits called but client not configured")
        return

    now = datetime.utcnow()
    period_end = now + timedelta(days=30)

    print(f"[SUPABASE] Refilling Pro credits for {user_id} to {amount}")

    try:
        supabase.table("user_credits").upsert(
            {
                "user_id": user_id,
                "credits": amount,
                "period_start": now.isoformat(),
                "period_end": period_end.isoformat(),
            }
        ).execute()
    except Exception as e:
        print(f"[SUPABASE] ERROR refilling user_credits: {e}")


def get_user_credits(user_id: str) -> dict | None:
    """
    Return the user_credits row or None.
    """
    if supabase is None:
        return None

    try:
        resp = (
            supabase.table("user_credits")
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        return resp.data
    except Exception as e:
        print(f"[SUPABASE] ERROR fetching user_credits for {user_id}: {e}")
        return None

# ----------------------------------------------------
# BILLING: get user plan
# ----------------------------------------------------
def get_user_plan(user_id: str):
    url = f"{SUPABASE_URL}/rest/v1/user_plans?user_id=eq.{user_id}&select=*"
    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        return None

    data = res.json()
    return data[0] if data else None


# ----------------------------------------------------
# Free usage tracking
# ----------------------------------------------------
def get_usage(user_id: str):
    url = f"{SUPABASE_URL}/rest/v1/usage_limits?user_id=eq.{user_id}&select=*"
    res = requests.get(url, headers=HEADERS)

    data = res.json()

    if not data:
        # Create record
        payload = {"user_id": user_id, "used_count": 0, "feature_type": "generic_ai"}
        requests.post(f"{SUPABASE_URL}/rest/v1/usage_limits", headers=HEADERS, json=payload)
        return payload

    return data[0]


def increment_usage(user_id: str):
    usage = get_usage(user_id)
    new_count = usage["used_count"] + 1

    url = f"{SUPABASE_URL}/rest/v1/usage_limits?user_id=eq.{user_id}"
    payload = {"used_count": new_count}

    requests.patch(url, headers=HEADERS, json=payload)


def deduct_credits(user_id: str, cost: int) -> int:
    """
    Deduct `cost` credits from the user, returns the new remaining balance.
    Raises ValueError if not enough credits.
    NOTE: This is a simple read-then-update (not strictly transactional),
    which is fine for low concurrency. For heavy scale, switch to a SQL RPC.
    """
    # 🔥 ADMIN BYPASS LOGIC
    if ADMIN_USER_ID and user_id == ADMIN_USER_ID:
        print(f"[ADMIN BYPASS] Skipping credit deduction for Admin User ID: {user_id}")
        return 999999 # Simulate a large balance
    
    # END ADMIN BYPASS
    if supabase is None:
        raise RuntimeError("Supabase not configured")

    row = get_user_credits(user_id)
    if row is None:
        # If no record, treat as 0 credits
        current = 0
    else:
        current = int(row.get("credits") or 0)

    if current < cost:
        raise ValueError(f"Not enough credits. Have {current}, need {cost}.")

    new_balance = current - cost
    print(
        f"[SUPABASE] Deducting {cost} credits from {user_id}. "
        f"{current} -> {new_balance}"
    )

    try:
        supabase.table("user_credits").update(
            {"credits": new_balance}
        ).eq("user_id", user_id).execute()
    except Exception as e:
        print(f"[SUPABASE] ERROR updating user_credits: {e}")
        # In a real system you might re-raise or handle more robustly
        raise

    return new_balance
