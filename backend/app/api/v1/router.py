from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.sources import router as sources_router
from app.api.v1.games import router as games_router
from app.api.v1.catalog import router as catalog_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.niches import router as niches_router
from app.api.v1.competitors import router as competitors_router
from app.api.v1.reviews_mining import router as reviews_mining_router
from app.api.v1.cross_platform import router as cross_platform_router
from app.api.v1.seasonality import router as seasonality_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, prefix="", tags=["Health"])
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_v1_router.include_router(sources_router, prefix="/sources", tags=["Data Sources"])
api_v1_router.include_router(games_router, prefix="/games", tags=["Games"])
api_v1_router.include_router(catalog_router, prefix="/catalog", tags=["Catalog"])
api_v1_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_v1_router.include_router(niches_router, prefix="/niches", tags=["Niches"])
api_v1_router.include_router(competitors_router, prefix="", tags=["Competitors"])
api_v1_router.include_router(reviews_mining_router, prefix="", tags=["Review Mining"])
api_v1_router.include_router(cross_platform_router, prefix="", tags=["PC Expansion"])
api_v1_router.include_router(seasonality_router, prefix="", tags=["Seasonality & Calendar"])
