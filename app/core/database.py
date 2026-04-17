from supabase import create_client, Client
from app.core.config import settings


def get_supabase_client() -> Client:
    """
    Initializes and returns the Supabase client.
    Fails safely if the environment variables are missing.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise ValueError(
            "Supabase URL and Anon Key must be configured in .env")

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


# Instantiate a global client to be imported by our services
supabase_db = get_supabase_client()
