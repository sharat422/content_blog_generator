from datetime import datetime, timedelta, timezone
from app.services.supabase_service import get_user_plan, get_usage, increment_usage

FREE_LIMIT = 2

def is_in_free_trial(user_data: dict) -> bool:
    """Check if user is within their first 7 days of account creation."""
    if not user_data or "created_at" not in user_data:
        return False
    
    try:
        # 1. GLOBAL GRACE PERIOD: Everyone gets a trial until Feb 13, 2026
        # (7 days from today, Feb 6, 2026)
        global_trial_end = datetime(2026, 2, 13, tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        
        if now <= global_trial_end:
            print(f"[DEBUG TRIAL] Global grace period active until {global_trial_end}")
            return True

        # 2. STANDARD TRIAL: 7 days from account creation
        created_at_str = user_data["created_at"]
        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        
        is_trial = now <= created_at + timedelta(days=7)
        print(f"[DEBUG TRIAL] User Created: {created_at}, Now: {now}, Is Trial: {is_trial}")
        return is_trial
    except Exception as e:
        print(f"[PERMISSIONS] Trial check error: {e}")
        return False

async def require_pro_for_twin(user_data: dict):
    """Twin feature allowed for PRO subscribers OR users in 7-day trial."""
    # 1. Check Free Trial
    if is_in_free_trial(user_data):
        return True

    # 2. Check Subscription
    user_id = user_data["id"]
    plan = get_user_plan(user_id)
    
    if not plan:
        return False
        
    # Check if plan is 'pro' and status is active/trialing
    is_pro = (plan.get("plan") or "").lower() == "pro"
    status = (plan.get("subscription_status") or "").lower()
    
    # If explicitly pro, allow it even if status is empty (for manual DB entries)
    if is_pro and (not status or status in {"active", "trialing", "past_due", "trial"}):
        return True
        
    return False


async def check_free_usage(user_id: str):
    """Verify if free user still has remaining uses."""
    usage = get_usage(user_id)

    used = usage["used_count"]
    if used >= FREE_LIMIT:
        return False

    increment_usage(user_id)
    return True
