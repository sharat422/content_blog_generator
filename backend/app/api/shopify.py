"""
shopify.py - /api/shopify router

Handles Shopify OAuth flow for WriteSwift.
"""
import os
import secrets
import urllib.parse
import hmac
import hashlib
import requests
import json

from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse

from app.services.security import verify_supabase_token
from app.services.shopify_service import save_shopify_store, register_webhooks, sync_initial_products, delete_shopify_data

router = APIRouter(prefix="/api/shopify", tags=["Shopify"])

SHOPIFY_CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID", "dummy_client_id")
SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET", "dummy_client_secret")
SHOPIFY_REDIRECT_URI = os.environ.get("SHOPIFY_REDIRECT_URI", "https://writeswift.ai/shopify/callback")

@router.get("/auth")
async def shopify_auth(request: Request, shop: str, user=Depends(verify_supabase_token)):
    """
    Initiate Shopify OAuth flow.
    Expected to be called by frontend to get the redirect URL.
    """
    if not shop:
        raise HTTPException(status_code=400, detail="Missing shop parameter")
    
    # Basic URL parsing and validation
    shop = shop.strip().lower()
    if "://" in shop:
        shop = shop.split("://")[1]
    if shop.endswith("/"):
        shop = shop[:-1]
    
    if not shop.endswith(".myshopify.com"):
        shop = f"{shop}.myshopify.com"

    # Generate random nonce
    state = secrets.token_hex(16)
    
    # Store in session (using string values for user sub to be safe)
    request.session["shopify_oauth_state"] = state
    request.session["shopify_shop"] = shop
    request.session["user_id"] = user.get("sub") if user else None
    
    # Construct OAuth URL
    scopes = "read_products,write_products,read_product_listings,read_publications,write_publications"
    
    params = {
        "client_id": SHOPIFY_CLIENT_ID,
        "scope": scopes,
        "redirect_uri": SHOPIFY_REDIRECT_URI,
        "state": state
    }
    
    auth_url = f"https://{shop}/admin/oauth/authorize?{urllib.parse.urlencode(params)}"
    
    return {"url": auth_url}

@router.get("/callback")
async def shopify_callback(request: Request, background_tasks: BackgroundTasks):
    """
    Handle the OAuth redirect back from Shopify.
    """
    query_params = dict(request.query_params)
    
    # Missing required parameters
    if "shop" not in query_params or "code" not in query_params or "state" not in query_params or "hmac" not in query_params:
        raise HTTPException(status_code=400, detail="Missing required query parameters")

    shop = query_params["shop"]
    code = query_params["code"]
    state = query_params["state"]
    received_hmac = query_params.pop("hmac")
    
    # 1. Verify HMAC
    sorted_params = "&".join([f"{k}={v}" for k, v in sorted(query_params.items())])
    calculated_hmac = hmac.new(
        SHOPIFY_CLIENT_SECRET.encode("utf-8"),
        sorted_params.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hmac, received_hmac):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature. Request may be spoofed.")

    # 2. Verify State (CSRF protection)
    session_state = request.session.get("shopify_oauth_state")
    user_id = request.session.get("user_id")
    
    if not session_state or state != session_state:
        raise HTTPException(status_code=400, detail="Invalid state parameter, possible CSRF")
        
    # Clear state from session
    if "shopify_oauth_state" in request.session:
        del request.session["shopify_oauth_state"]
        
    # 3. Exchange code for access token
    token_url = f"https://{shop}/admin/oauth/access_token"
    token_payload = {
        "client_id": SHOPIFY_CLIENT_ID,
        "client_secret": SHOPIFY_CLIENT_SECRET,
        "code": code
    }
    
    try:
        response = requests.post(token_url, json=token_payload)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise ValueError("No access token returned from Shopify")
            
    except Exception as e:
        print(f"[SHOPIFY] Error exchanging token for {shop}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve access token from Shopify")

    # 4. Save store & token in database
    if user_id:
        save_shopify_store(shop, access_token, user_id)
    else:
        print(f"[SHOPIFY] WARNING: No user_id in session. Saving store {shop} without explicit owner.")
        save_shopify_store(shop, access_token, "unknown")
        
    # 5. Register Webhooks and trigger background product sync
    # We do this asynchronously to avoid making the user wait
    background_tasks.add_task(register_webhooks, shop, access_token)
    background_tasks.add_task(sync_initial_products, shop, access_token)
    
    # Redirect merchant back to WriteSwift dashboard
    app_base_url = os.getenv("VITE_API_URL", "https://writeswift.ai").replace("/api", "")
    return RedirectResponse(url=f"{app_base_url}/ecommerce?connected={shop}")

@router.get("/status")
async def check_shopify_status(user=Depends(verify_supabase_token)):
    """
    Check if the current user has a connected Shopify store.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    user_id = user.get("sub")
    
    from app.services.supabase_service import supabase
    if not supabase:
        raise HTTPException(status_code=500, detail="Database disabled")
        
    response = supabase.table("shopify_stores").select("shop_domain").eq("user_id", user_id).limit(1).execute()
    
    if response.data and len(response.data) > 0:
        return {"connected": True, "shop_domain": response.data[0]["shop_domain"]}
        
    return {"connected": False}

@router.get("/products")
async def get_shopify_products(shop: str, user=Depends(verify_supabase_token)):
    """
    Get the cached list of products for the connected store.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    from app.services.supabase_service import supabase
    if not supabase:
        raise HTTPException(status_code=500, detail="Database disabled")
        
    # Verify the user actually owns this shop (rudimentary check context)
    user_id = user.get("sub")
    store_check = supabase.table("shopify_stores").select("shop_domain").eq("user_id", user_id).eq("shop_domain", shop).execute()
    
    if not store_check.data or len(store_check.data) == 0:
        raise HTTPException(status_code=403, detail="Not authorized to view products for this shop")
    
    # Fetch cached products
    response = supabase.table("shopify_products").select("*").eq("shop_domain", shop).execute()
    
    return {"products": response.data or []}

from pydantic import BaseModel

class PublishProductRequest(BaseModel):
    shop_domain: str
    product_id: str
    description_html: str
    meta_title: str = None
    meta_description: str = None

@router.post("/publish-product")
async def publish_shopify_product(req: PublishProductRequest, user=Depends(verify_supabase_token)):
    """
    1-click publish from the SplitPaneEditor directly to Shopify.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    from app.services.supabase_service import supabase
    if not supabase:
        raise HTTPException(status_code=500, detail="Database disabled")
        
    # Verify the user actually owns this shop
    user_id = user.get("sub")
    store_check = supabase.table("shopify_stores").select("access_token").eq("user_id", user_id).eq("shop_domain", req.shop_domain).execute()
    
    if not store_check.data or len(store_check.data) == 0:
        raise HTTPException(status_code=403, detail="Not authorized to edit products for this shop")
        
    access_token = store_check.data[0]["access_token"]
    
    from app.services.shopify_service import push_product_update
    success, error = await push_product_update(
        req.shop_domain, 
        access_token, 
        req.product_id, 
        req.description_html, 
        req.meta_title, 
        req.meta_description
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to publish to Shopify: {error}")
        
    # Optionally update the Supabase cache here so the UI reflects "Published"
    try:
        supabase.table("shopify_products").update({
            "internal_status": "published", 
            "description": req.description_html
        }).eq("product_id", req.product_id).execute()
    except Exception as e:
        print(f"[SHOPIFY] Failed to update local cache status to published: {e}")
        
    return {"success": True}

@router.post("/webhook/uninstalled")
async def shopify_webhook_uninstalled(request: Request):
    """
    Handle Shopify app/uninstalled webhook.
    Clean up access tokens and caches.
    """
    raw_body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")
    shop_domain = request.headers.get("X-Shopify-Shop-Domain")
    
    if not hmac_header or not shop_domain:
        raise HTTPException(status_code=400, detail="Missing webhook headers")
        
    # Verify Webhook HMAC
    import base64
    calculated_hmac = base64.b64encode(
        hmac.new(
            SHOPIFY_CLIENT_SECRET.encode("utf-8"),
            raw_body,
            hashlib.sha256
        ).digest()
    ).decode("utf-8")
    
    if not hmac.compare_digest(calculated_hmac, hmac_header):
        raise HTTPException(status_code=401, detail="Invalid webhook HMAC")
        
    # Valid webhook, delete shop data
    delete_shopify_data(shop_domain)
    
    return JSONResponse(content={"status": "ok"})
