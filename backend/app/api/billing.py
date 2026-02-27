# ============================================================
#   billing.py — Optimized & Production-Safe Version
# ============================================================

import os
from typing import Optional, Dict, Any

import stripe
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from app.services.security import verify_supabase_token
from app.services.supabase_service import (
    set_user_plan,
    supabase,
    refill_pro_credits,
)

router = APIRouter(prefix="/api/billing", tags=["Billing"])

# ------------------------------------------------------------
# Stripe Environment Setup
# ------------------------------------------------------------
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
DEFAULT_PRICE_ID_PRO = os.getenv("STRIPE_PRICE_ID_PRO")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:3000")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY
    print("[OK] Stripe initialized")
else:
    print("[ERROR] STRIPE_SECRET_KEY missing! Stripe will not work.")
if not STRIPE_SECRET_KEY:
    raise RuntimeError("STRIPE_SECRET_KEY is missing")

IS_LIVE = STRIPE_SECRET_KEY.startswith("sk_live_")

if os.getenv("ENVIRONMENT") == "production" and not IS_LIVE:
    raise RuntimeError("[CRITICAL] Test Stripe key used in PRODUCTION")

class PaymentRequest(BaseModel):
    price_id: Optional[str] = None


class CheckoutResponse(BaseModel):
    checkout_url: str

# Treat these subscription states as "already subscribed"
ACTIVE_SUB_STATUSES = ("active", "trialing", "past_due")

def get_user_plan_row(user_id: str):
    """
    Returns a row from user_plans or None
    """
    try:
        resp = (
            supabase.table("user_plans")
            .select("plan, subscription_status, stripe_customer_id, stripe_subscription_id")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        if resp is None:
            print("[WARN] Supabase execute() returned None in get_user_plan_row")
            return None

        # supabase-py response normally has .data and .error
        err = getattr(resp, "error", None)
        if err:
            print("[WARN] Supabase error in get_user_plan_row:", err)
            return None

        data = getattr(resp, "data", None)
        return data or None

    except Exception as e:
        print("[ERROR] Exception in get_user_plan_row:", repr(e))
        return None


# ------------------------------------------------------------
# Checkout Session Creation
# ------------------------------------------------------------
@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    payment: PaymentRequest,
    user: Dict[str, Any] = Depends(verify_supabase_token),
):
    """Create Stripe Checkout session for subscription."""

    price_id = payment.price_id or DEFAULT_PRICE_ID_PRO
    #print(f"--> Using default price ID: {price_id}")
    #print(f"{payment}")
    if not price_id:
        raise HTTPException(400, "Missing price_id")

    email = user.get("email")
    user_id = user.get("id")
   
    # If already subscribed, do NOT send them to checkout again.
    row = get_user_plan_row(user_id)
    if row and row.get("plan") == "pro" and row.get("subscription_status") in ACTIVE_SUB_STATUSES:
        customer_id = row.get("stripe_customer_id")
        if customer_id:
            portal = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=f"{APP_BASE_URL}/pricing",
           )
           # return checkout_url so frontend can redirect as usual
            return {"checkout_url": portal.url}

    # If somehow missing customer id, block duplicate subscription
        raise HTTPException(409, "Already subscribed")

    #print("\n==== /checkout START ====")
    #print(f"User: {user_id} ({email})")
    #print(f"Price ID: {price_id}")

    # Ensure customer exists
    try:
        result = stripe.Customer.list(email=email, limit=1)
        if result.data:
            customer = result.data[0]
           # print(f"--> Existing customer: {customer.id}")

            stripe.Customer.modify(
                customer.id,
                metadata={"supabase_user_id": user_id, "email": email},
            )
        else:
            customer = stripe.Customer.create(
                email=email,
                metadata={"supabase_user_id": user_id, "email": email},
            )
           # print(f"--> Created new customer: {customer.id}")

    except Exception as e:
        print("[ERROR] Error preparing Stripe customer", e)
        raise HTTPException(500, "Stripe customer error")

    # Create a checkout session
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer.id,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{APP_BASE_URL}/pricing?status=success",
            cancel_url=f"{APP_BASE_URL}/pricing?status=cancel",
            metadata={
                "supabase_user_id": user_id,
                "supabase_email": email,
            },
        )
       # print("--> Checkout session created:", session.id)
        return {"checkout_url": session.url}

    except Exception as e:
        print("[ERROR] Checkout error: ", e)
        raise HTTPException(500, "Stripe checkout error")
# ------------------------------------------------------------
# Billing Status (Frontend uses this to hide/disable Pro)
# ------------------------------------------------------------
@router.get("/status")
async def billing_status(user: Dict[str, Any] = Depends(verify_supabase_token)):
    user_id = user.get("id")
    row = get_user_plan_row(user_id)
    if not row :
       return {"plan": "free", "subscription_status": None }
    return row
# ------------------------------------------------------------
# Billing Portal
# ------------------------------------------------------------
@router.post("/portal")
async def billing_portal(user=Depends(verify_supabase_token)):
    user_id = user["id"]

    resp = (
        supabase.table("user_plans")
        .select("stripe_customer_id")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )

    customer_id = resp.data.get("stripe_customer_id")
    if not customer_id:
        raise HTTPException(400, "No Stripe customer found for user")

    portal = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{APP_BASE_URL}/account/billing",
    )
    return {"url": portal.url}


# ------------------------------------------------------------
# Helper: Extract Metadata Safely
# ------------------------------------------------------------
def extract_user_id(data: Dict[str, Any], customer_id: Optional[str]):
    """
    Stripe events sometimes place metadata under:
    - subscription.metadata
    - invoice.metadata
    - checkout.session.metadata
    If missing, fallback to fetching metadata from customer object.
    """

    metadata = data.get("metadata") or {}

    supabase_user_id = metadata.get("supabase_user_id")

    if supabase_user_id:
        return supabase_user_id

    # fallback → fetch customer metadata
    if customer_id:
        try:
            cust = stripe.Customer.retrieve(customer_id)
            cm = cust.get("metadata") or {}
            uid = cm.get("supabase_user_id")
            if uid:
                print(f"--> Resolved user from customer metadata: {uid}")
                return uid
        except Exception as e:
            print("[WARN] Could not retrieve customer metadata", e)

    print("[WARN] No supabase_user_id found anywhere")
    return None


# ------------------------------------------------------------
# Stripe Webhook
# ------------------------------------------------------------
@router.post("/webhook")
async def stripe_webhook(request: Request):

    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        print("[ERROR] Invalid webhook signature:", e)
        raise HTTPException(400, "Invalid signature")

    event_type = event["type"]
    data = event["data"]["object"]

    #print("\n============ 🔔 STRIPE WEBHOOK ============")
    #print("Event:", event_type)

    # ------------------------------
    # Subscription Created / Updated
    # ------------------------------
    if event_type in ("customer.subscription.created", "customer.subscription.updated"):

        customer_id = data.get("customer")
        subscription_id = data.get("id")
        status = data.get("status")

        user_id = extract_user_id(data, customer_id)
        if not user_id:
            return {"received": True}

        plan = "pro" if status in ("active", "trialing", "past_due") else "free"

        set_user_plan(
            user_id=user_id,
            plan=plan,
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            subscription_status=status,
        )

       # print(f"--> Updated plan → {user_id} → {plan}")
        return {"received": True}

    # ------------------------------
    # Subscription Deleted
    # ------------------------------
    if event_type == "customer.subscription.deleted":

        customer_id = data.get("customer")
        subscription_id = data.get("id")

        user_id = extract_user_id(data, customer_id)
        if not user_id:
            return {"received": True}

        set_user_plan(
            user_id=user_id,
            plan="free",
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            subscription_status="canceled",
        )

        print("--> Subscription canceled for", user_id)
        return {"received": True}

    # ------------------------------
    # Invoice Paid → refill credits
    # ------------------------------
    if event_type in ("invoice.payment_succeeded", "invoice.paid"):

        customer_id = data.get("customer")
        subscription_id = data.get("subscription")
        status = data.get("status")

        user_id = extract_user_id(data, customer_id)
        if not user_id:
            return {"received": True}

        # update plan
        set_user_plan(
            user_id=user_id,
            plan="pro",
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            subscription_status=status,
        )

        # refill credits
        print(f"--> Refill credits for {user_id}")
        refill_pro_credits(user_id)

        return {"received": True}

    # ------------------------------
    # Unhandled events (ignored)
    # ------------------------------
    print("[INFO] Unhandled event:", event_type)
    return {"received": True}
