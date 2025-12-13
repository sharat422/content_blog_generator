from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

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
        print("❌ No token provided.")
        raise credentials_exception()

    userinfo_url = f"{SUPABASE_URL}/auth/v1/user"
    print("🌍 Checking token via:", userinfo_url)

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
        print("❌ Supabase rejected token.")
        raise credentials_exception()

    user = response.json()
    #print("✅ Supabase token verified:", user)
   # print("========================================================\n")

    return user

# -----------------------------------------------------------
# Backward compatibility for billing.py
# -----------------------------------------------------------
def verify_supabase_token(token: str = Depends(oauth2_scheme)):
    return get_current_user(token)
