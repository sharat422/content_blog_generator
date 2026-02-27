# app/config/credit_costs.py
# Credit costs for generate.py and other consumers that import
# from app.config.credit_costs

CREDIT_COSTS = {
    "text": 5,
    "image": 20,
    "video_script": 8,
    "outline": 3,
    "video_render": 100,
}


def get_cost(action_type: str) -> int:
    return CREDIT_COSTS.get(action_type, 5)
