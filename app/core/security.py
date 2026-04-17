# backend/app/core/security.py
import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from app.core.config import settings

security = HTTPBearer()


def get_user_db_client(credentials: HTTPAuthorizationCredentials = Security(security)) -> tuple[Client, str]:
    token = credentials.credentials

    if not settings.SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=500, detail="JWT Secret not configured.")

    try:
        # Cryptographically verify the token locally (Zero Latency)
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token payload.")

        # Inject the token into the Supabase client for Row Level Security
        client = create_client(settings.SUPABASE_URL,
                               settings.SUPABASE_ANON_KEY)
        client.postgrest.auth(token)

        return client, user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, detail="Authentication token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401, detail=f"Invalid authentication token: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Authentication failed: {str(e)}")
