# app/core/costs.py

# -----------------------------
# Credit Cost Table
# -----------------------------
credit_costs = {
    "Blog Post": 5,
    "YouTube Script": 5,
    "Ad Copy": 2,
    "Short Video Idea": 2,
    "Image Generation": 10,
    "Default": 5
}


# -----------------------------
# Function: Get cost for template
# -----------------------------
def get_cost(template: str) -> int:
    """
    Return credit cost for the selected template.
    If template not found, fallback to default cost.
    """
    return credit_costs.get(template, credit_costs["Default"])
