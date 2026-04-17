import logging
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.schemas.cards import LearningDeckRequest, LearningDeckResponse
from app.services.graph_service import get_existing_skills_for_strand
from app.services.llm_service import generate_learning_deck
from app.core.security import get_user_db_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate-deck", response_model=LearningDeckResponse)
async def create_learning_deck(
    request: LearningDeckRequest,
    db_data: tuple[Client, str] = Depends(get_user_db_client)
):
    try:
        # 1. Fetch existing skills from Neo4j to enforce Data Governance
        existing_skills = await get_existing_skills_for_strand(request.chosen_lens)

        # 2. Generate the 3-Card Deck using Gemini
        deck = await generate_learning_deck(
            object_name=request.object_name,
            strand=request.chosen_lens,
            grade_level=request.grade_level,
            existing_skills=existing_skills
        )

        return deck

    except RuntimeError as e:
        logger.error(f"Deck Generation Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate the learning deck. The AI might be overloaded."
        )
    except Exception as e:
        logger.error(f"Unexpected error in /generate-deck: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred."
        )
