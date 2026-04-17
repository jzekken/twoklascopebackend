from fastapi import APIRouter
from app.api.v1.endpoints import discover, chat, pathfinder, learn

api_router = APIRouter()

api_router.include_router(
    discover.router, prefix="/discover", tags=["Discovery"])

api_router.include_router(
    chat.router, prefix="/chat", tags=["Tutor API"])

api_router.include_router(
    pathfinder.router, prefix="/pathfinder", tags=["Pathfinder Engine"])

api_router.include_router(
    learn.router, prefix="/learn", tags=["Learning Cards"])
