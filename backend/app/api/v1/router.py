from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.sources import router as sources_router
from app.api.v1.games import router as games_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, prefix="", tags=["Health"])
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_v1_router.include_router(sources_router, prefix="/sources", tags=["Data Sources"])
api_v1_router.include_router(games_router, prefix="/games", tags=["Games"])
