import os
import requests
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv, find_dotenv
env_path = find_dotenv()
print("[DEBUG SECURITY.PY] find_dotenv returned:", env_path)
load_dotenv(env_path)
# -----------------------------------------------------------
# Environment Variables
# -----------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")  # publishable key

#print("🔧 SUPABASE_URL:", SUPABASE_URL)
#print("🔧 Using Publishable Key:", bool(SUPABASE_ANON_KEY))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="not-used")

def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

# -----------------------------------------------------------
# ⭐ OFFICIAL /auth/v1/user VALIDATION
# No JWKS needed — Supabase handles it internally
# -----------------------------------------------------------
def get_current_user(token: str = Depends(oauth2_scheme)):
    #print("\n================= 🔎 DEBUG TOKEN CHECK =================")
    #print("🔍 Incoming Bearer Token (truncated):", token[:60] + "...")

    if not token:
        print("[ERROR] No token provided.")
        raise credentials_exception()

    userinfo_url = f"{SUPABASE_URL}/auth/v1/user"
    print("Checking token via:", userinfo_url)
    print("DEBUG ENV SUPABASE_URL:", os.getenv("SUPABASE_URL"))
    print("DEBUG GLOBAL SUPABASE_URL:", SUPABASE_URL)

    response = requests.get(
        userinfo_url,
        headers={
            "Authorization": f"Bearer {token}",
            "apikey": SUPABASE_ANON_KEY
        }
    )

    #print("🔍 AUTH USER CHECK STATUS:", response.status_code)
    #print("🔍 AUTH USER RESPONSE:", response.text)

    if response.status_code != 200:
        print("[ERROR] Supabase rejected token.")
        raise credentials_exception()

    user = response.json()
    print(f"[DEBUG AUTH] User keys: {list(user.keys())}")
    if "created_at" in user:
        print(f"[DEBUG AUTH] created_at: {user['created_at']}")
    #print("[OK] Supabase token verified:", user)
   # print("========================================================\n")

    return user

# -----------------------------------------------------------
# Backward compatibility for billing.py
# -----------------------------------------------------------
def verify_supabase_token(token: str = Depends(oauth2_scheme)):
    return get_current_user(token)
