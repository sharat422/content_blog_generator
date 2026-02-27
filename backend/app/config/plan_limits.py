PLAN_LIMITS = {
    "free": {
        "generations": 10,
        "words": 5000,  # optional
    },
    "pro": {
        "generations": 50000,
        "words": 50000,
    }
}

CREDIT_COSTS = {
    "text": 5,
    "image": 20,
    "video_script": 8,
    "outline": 3
}

def get_cost(action_type: str):
    return CREDIT_COSTS.get(action_type, 5)


def get_limits(plan: str):
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
