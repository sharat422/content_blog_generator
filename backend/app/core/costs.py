# app/core/costs.py

# -----------------------------
# Credit Cost Table
# -----------------------------
credit_costs = {
    # General templates
    "Blog Post": 5,
    "YouTube Script": 5,
    "Ad Copy": 2,
    "Short Video Idea": 2,
    "Image Generation": 10,
    # Ecommerce SEO templates
    "Ecommerce Product Description": 5,
    "Ecommerce Blog Post": 5,
    "Marketplace Listing": 6,
    "Category Page": 4,
    "Product FAQ": 3,
    "Meta Tags": 2,
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
