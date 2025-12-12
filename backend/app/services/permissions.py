from app.services.supabase_service import get_user_plan, get_usage, increment_usage

FREE_LIMIT = 2

async def require_pro_for_twin(user_id: str):
    """Twin feature only for PRO subscribers."""
    plan = get_user_plan(user_id)
    
    if not plan or plan.get("is_pro") != True:
        return False  # not allowed
    
    return True


async def check_free_usage(user_id: str):
    """Verify if free user still has remaining uses."""
    usage = get_usage(user_id)

    used = usage["used_count"]
    if used >= FREE_LIMIT:
        return False

    increment_usage(user_id)
    return True
