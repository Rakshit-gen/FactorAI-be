from fastapi import Header, HTTPException
from typing import Optional
import jwt
import os
import requests
from functools import lru_cache

# Cache the JWKS for 1 hour
@lru_cache(maxsize=1)
def get_clerk_jwks():
    """Fetch Clerk's public keys for JWT verification"""
    clerk_domain = os.getenv("CLERK_DOMAIN", "clerk.your-domain.com")
    jwks_url = f"https://{clerk_domain}/.well-known/jwks.json"
    
    try:
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching JWKS: {e}")
        return None

def verify_clerk_token(token: str) -> dict:
    """Verify Clerk JWT token"""
    
    # For development only - skip verification
    if os.getenv("ENVIRONMENT") == "development":
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token decode failed: {str(e)}")
    
    # Production - verify with Clerk's public key
    try:
        from jwt import PyJWKClient
        
        clerk_domain = os.getenv("CLERK_DOMAIN")
        if not clerk_domain:
            raise HTTPException(status_code=500, detail="CLERK_DOMAIN not configured")
        
        jwks_url = f"https://{clerk_domain}/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        
        # Get the signing key
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Verify and decode
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True}
        )
        
        return decoded
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """Extract and verify user from authorization header"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        decoded = verify_clerk_token(token)
        user_id = decoded.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        
        return user_id
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")