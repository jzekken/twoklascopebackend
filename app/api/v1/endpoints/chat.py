from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_tutor_response
from app.core.security import get_user_db_client

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_with_tutor(
    request: ChatRequest,
    # Lock this route down! Only authenticated Flutter users can talk to the tutor.
    db_data: tuple[Client, str] = Depends(get_user_db_client)
):
    try:
        # db_client and user_id are available here to save chat logs to Supabase later
        db_client, user_id = db_data

        reply_text = await generate_tutor_response(request)

        return ChatResponse(reply=reply_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
