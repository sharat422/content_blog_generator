# app/services/shopify_service.py
import os
import requests
import json
from .supabase_service import SUPABASE_URL, HEADERS, supabase

# Ideally, access tokens should be encrypted before storage. 
# For this implementation, we will store them securely in the restricted Supabase table
# assuming Row Level Security is configured to prevent unauthorized reads.

def save_shopify_store(shop: str, access_token: str, user_id: str):
    """
    Store the token in the `shopify_stores` table.
    """
    if supabase is None:
        print("[SHOPIFY_SERVICE] Supabase client not initialized")
        return
        
    data = {
        "shop_domain": shop,
        "access_token": access_token, 
        "user_id": user_id
    }
    
    try:
        supabase.table("shopify_stores").upsert(data, on_conflict="shop_domain").execute()
        print(f"[SHOPIFY_SERVICE] Saved access token for {shop}")
    except Exception as e:
        print(f"[SHOPIFY_SERVICE] ERROR saving store token for {shop}: {e}")
        
def register_webhooks(shop: str, access_token: str):
    """
    Register the app/uninstalled webhook to clean up access tokens later.
    """
    api_version = "2024-04" 
    url = f"https://{shop}/admin/api/{api_version}/webhooks.json"
    
    # We will need the app's base URL dynamically
    app_base_url = os.getenv("VITE_API_URL", "https://writeswift.ai")
    if "localhost" in app_base_url or "127.0.0.1" in app_base_url:
        print("[SHOPIFY_SERVICE] Cannot register webhook on localhost without ngrok/tunnel.")
        return
        
    webhook_payload = {
        "webhook": {
            "topic": "app/uninstalled",
            "address": f"{app_base_url}/api/shopify/webhook/uninstalled",
            "format": "json"
        }
    }
    
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=webhook_payload)
        response.raise_for_status()
        print(f"[SHOPIFY_SERVICE] Successfully registered app/uninstalled webhook for {shop}")
    except Exception as e:
        print(f"[SHOPIFY_SERVICE] ERROR registering webhook for {shop}: {e}")
        if isinstance(e, requests.exceptions.HTTPError):
            print(f"[{e.response.status_code}] {e.response.text}")

import asyncio

async def _execute_graphql(shop: str, access_token: str, query: str, variables: dict = None):
    """
    Executes a GraphQL query against the Shopify Admin API.
    Handles cost-based rate limiting proactively.
    """
    api_version = "2024-04"
    url = f"https://{shop}/admin/api/{api_version}/graphql.json"
    
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    
    # Check for GraphQL errors
    if "errors" in data:
        print(f"[SHOPIFY_SERVICE] GraphQL Errors for {shop}: {data['errors']}")
        raise Exception(f"GraphQL Errors: {data['errors']}")
        
    # Handle rate limit cost proactively
    extensions = data.get("extensions", {})
    cost = extensions.get("cost", {})
    throttleStatus = cost.get("throttleStatus", {})
    
    currently_available = throttleStatus.get("currentlyAvailable", 1000)
    restore_rate = throttleStatus.get("restoreRate", 50)
    requested_query_cost = cost.get("requestedQueryCost", 0)

    # If we are dipping too low, proactively sleep before returning 
    # so the next call in the loop won't get a 429 Error.
    if currently_available < requested_query_cost * 2 and currently_available < 100:
        # We need more points. Let's wait for at least requested_query_cost points to regenerate
        points_needed = max(0, requested_query_cost - currently_available + 50)
        sleep_time = points_needed / restore_rate
        print(f"[SHOPIFY_SERVICE] Cost limit approaching on {shop}. 100 max, Currently available: {currently_available}, Cost: {requested_query_cost}. Sleeping for {sleep_time:.2f}s...")
        await asyncio.sleep(sleep_time)
        
    return data

async def sync_initial_products(shop: str, access_token: str):
    """
    Fetch the complete product catalog via GraphQL API (paginated) and cache them in DB.
    """
    # First clear old cache for this shop if doing a full sync
    if supabase:
        supabase.table("shopify_products").delete().eq("shop_domain", shop).execute()

    query = """
    query GetProducts($cursor: String) {
      products(first: 250, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            id
            title
            descriptionHtml
            handle
            status
            productType
            tags
            variants(first: 1) {
              edges {
                node {
                  price
                }
              }
            }
            images(first: 1) {
              edges {
                node {
                  url
                }
              }
            }
          }
        }
      }
    }
    """
    
    has_next_page = True
    cursor = None
    total_fetched = 0
    
    try:
        while has_next_page:
            variables = {"cursor": cursor} if cursor else {}
            data = await _execute_graphql(shop, access_token, query, variables)
            
            products_page = data.get("data", {}).get("products", {})
            edges = products_page.get("edges", [])
            page_info = products_page.get("pageInfo", {})
            
            if not edges:
                break
                
            products_to_cache = []
            for edge in edges:
                node = edge.get("node", {})
                
                # Extract image url if exists
                image_url = None
                images_edges = node.get("images", {}).get("edges", [])
                if images_edges:
                    image_url = images_edges[0].get("node", {}).get("url")
                    
                # Extract price if exists
                price = None
                variant_edges = node.get("variants", {}).get("edges", [])
                if variant_edges:
                    price = variant_edges[0].get("node", {}).get("price")
                
                products_to_cache.append({
                    "shop_domain": shop,
                    "product_id": node.get("id"),
                    "title": node.get("title"),
                    "description": node.get("descriptionHtml"),
                    "handle": node.get("handle"),
                    "status": node.get("status"),
                    "product_type": node.get("productType"),
                    "tags": node.get("tags"),
                    "image_url": image_url,
                    "price": price
                })
                
            if products_to_cache and supabase:
                supabase.table("shopify_products").insert(products_to_cache).execute()
                
            total_fetched += len(products_to_cache)
            has_next_page = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor")
            
        print(f"[SHOPIFY_SERVICE] Successfully synced {total_fetched} products for {shop}")
            
    except Exception as e:
        print(f"[SHOPIFY_SERVICE] ERROR syncing products for {shop}: {e}")

async def fetch_single_product(shop: str, access_token: str, product_id: str) -> dict:
    """
    Fetch a single product's fresh data from Shopify during a live editing session.
    """
    query = """
    query GetProduct($id: ID!) {
      product(id: $id) {
        id
        title
        descriptionHtml
        handle
        status
        tags
        seo {
          title
          description
        }
      }
    }
    """
    
    # Ensure ID is formatted globally (gid://)
    if not product_id.startswith("gid://shopify/Product/"):
        product_id = f"gid://shopify/Product/{product_id}"
        
    try:
        data = await _execute_graphql(shop, access_token, query, {"id": product_id})
        return data.get("data", {}).get("product", {})
    except Exception as e:
        print(f"[SHOPIFY_SERVICE] ERROR fetching single product {product_id} for {shop}: {e}")
        return None

async def push_product_update(shop: str, access_token: str, product_id: str, description_html: str, meta_title: str = None, meta_desc: str = None):
    """
    1-click publish path replacing manual copy/paste. Updates product description and SEO metadata.
    """
    mutation = """
    mutation UpdateProduct($input: ProductInput!) {
      productUpdate(input: $input) {
        product {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    
    if not product_id.startswith("gid://shopify/Product/"):
        product_id = f"gid://shopify/Product/{product_id}"
        
    input_data = {
        "id": product_id,
        "descriptionHtml": description_html,
    }
    
    if meta_title or meta_desc:
        input_data["seo"] = {}
        if meta_title:
            input_data["seo"]["title"] = meta_title
        if meta_desc:
            input_data["seo"]["description"] = meta_desc
            
    try:
        data = await _execute_graphql(shop, access_token, mutation, {"input": input_data})
        errors = data.get("data", {}).get("productUpdate", {}).get("userErrors", [])
        if errors:
            print(f"[SHOPIFY_SERVICE] Validation Errors updating product {product_id}: {errors}")
            return False, errors
            
        print(f"[SHOPIFY_SERVICE] Successfully updated product {product_id} on {shop}")
        return True, None
    except Exception as e:
        print(f"[SHOPIFY_SERVICE] ERROR updating product {product_id} for {shop}: {e}")
        return False, str(e)

async def trigger_bulk_publish(shop: str, access_token: str, jsonl_url: str):
    """
    Trigger a bulk operation run mutation fetching from an uploaded JSONL file.
    Note: Requires uploading the file to Shopify stagedUploads first in a real scenario.
    """
    mutation = """
    mutation bulkOperationRunMutation($mutation: String!, $stagedUploadPath: String!) {
      bulkOperationRunMutation(
        mutation: $mutation,
        stagedUploadPath: $stagedUploadPath
      ) {
        bulkOperation {
          id
          url
          status
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    
    # The actual mutation we want bulk applied to every line in the JSONL
    inner_mutation = """
    mutation UpdateProductBulk($input: ProductInput!) {
      productUpdate(input: $input) {
        product {
          id
        }
      }
    }
    """
    
    # STUB: Ideally we first call stagedUploadsCreate to generate an S3 URL,
    # upload our JSONL there using those exact credentials, then pass that path here.
    # For now, we simulate passing the path if we had it.
    staged_path = "tmp/placeholder-path.jsonl"
    
    try:
        data = await _execute_graphql(shop, access_token, mutation, {
            "mutation": inner_mutation,
            "stagedUploadPath": staged_path
        })
        op = data.get("data", {}).get("bulkOperationRunMutation", {}).get("bulkOperation", {})
        print(f"[SHOPIFY_SERVICE] Triggered Bulk Mutation on {shop}: {op.get('id')} - Status {op.get('status')}")
        return op
    except Exception as e:
        print(f"[SHOPIFY_SERVICE] ERROR triggering bulk operation on {shop}: {e}")
        return None

def delete_shopify_data(shop: str):
    """
    Delete shopify token and cache data on uninstall.
    """
    if supabase is None:
        return
        
    try:
        print(f"[SHOPIFY_SERVICE] Deleting all data for uninstalled shop {shop}")
        supabase.table("shopify_stores").delete().eq("shop_domain", shop).execute()
        supabase.table("shopify_products").delete().eq("shop_domain", shop).execute()
    except Exception as e:
        print(f"[SHOPIFY_SERVICE] ERROR deleting data for {shop}: {e}")
