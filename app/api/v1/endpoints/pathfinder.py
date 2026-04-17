from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.schemas.pathfinder import PathfinderResponse
from app.services.graph_service import get_user_skill_web
from app.services.llm_service import generate_holistic_pathfinder
from app.core.security import get_user_db_client

router = APIRouter()


@router.get("/recommend", response_model=PathfinderResponse)
async def get_career_recommendations(
    db_data: tuple[Client, str] = Depends(get_user_db_client)
):
    try:
        _, user_id = db_data

        # 1. Ask Neo4j for the complete Skill Web
        skill_web = await get_user_skill_web(user_id)

        if not skill_web:
            raise HTTPException(
                status_code=404,
                detail="Not enough data. Scan objects to build your Kaalaman Skill Tree first!"
            )

        # 2. Ask Gemini to synthesize the web into the 3 Tiers
        recommendations = await generate_holistic_pathfinder(
            xp_distribution=skill_web["xp_distribution"],
            top_skills=skill_web["top_skills"]
        )

        return recommendations

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
