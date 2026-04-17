from qdrant_client import QdrantClient
from app.core.config import settings


def get_qdrant_client() -> QdrantClient | None:
    """
    Initializes the Qdrant Vector DB client.
    Fails safely if credentials are not yet added to the .env file.
    """
    if not settings.QDRANT_URL or not settings.QDRANT_API_KEY:
        print("Warning: Qdrant credentials missing. Running Tutor in standard LLM mode without Vector Search.")
        return None

    return QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)


qdrant_db = get_qdrant_client()
