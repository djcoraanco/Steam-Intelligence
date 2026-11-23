from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.config import settings
from app.schemas.health import HealthResponse, ComponentHealth

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    """Health status of the API and its backing services."""
    components = {}

    # Check database
    try:
        db.execute(text("SELECT 1"))
        components["database"] = ComponentHealth(
            status="healthy",
            details={"type": "relational_db", "connected": True}
        )
    except Exception as exc:
        components["database"] = ComponentHealth(
            status="unavailable",
            details={"type": "relational_db", "connected": False, "error": str(exc)}
        )

    # Check steam connector status
    components["steam_provider"] = ComponentHealth(
        status="configured" if settings.STEAM_WEB_API_KEY else "unauthenticated_public_only",
        details={
            "base_url": settings.STEAM_API_BASE_URL,
            "has_api_key": bool(settings.STEAM_WEB_API_KEY)
        }
    )

    overall_status = "ok" if components["database"].status == "healthy" else "degraded"

    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        environment=settings.APP_ENV,
        timestamp=datetime.now(timezone.utc),
        components=components
    )


@router.get("/ready")
def get_readiness(db: Session = Depends(get_db)):
    """Kubernetes/Docker readiness check."""
    try:
        db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception as exc:
        return {"ready": False, "reason": str(exc)}
