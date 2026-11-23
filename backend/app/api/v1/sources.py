from datetime import datetime, timezone
import time
from typing import List
import uuid
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.sources import DataSource
from app.schemas.sources import DataSourceResponse, DataSourceTestResult
from app.connectors.registry import CONNECTORS_METADATA

router = APIRouter()


@router.get("", response_model=List[DataSourceResponse])
def list_sources(db: Session = Depends(get_db)):
    """List all registered and configured data sources."""
    # Ensure all data sources from registry exist in the DB
    sources = db.query(DataSource).all()
    if not sources:
        # Seed sources from metadata
        for meta in CONNECTORS_METADATA:
            ds = DataSource(
                id=uuid.uuid4(),
                code=meta["provider_code"],
                name=meta["provider_name"],
                provider_type=meta["provider_type"],
                status=meta["status"],
                capabilities=meta["capabilities"],
                base_url=meta.get("base_url"),
                documentation_url=meta.get("documentation_url"),
                terms_url=meta.get("terms_url"),
                rate_limit_config={"policy": meta.get("rate_limit_policy", "standard")},
                last_verified_at=None,
                created_at=datetime.now(timezone.utc)
            )
            db.add(ds)
        db.commit()
        sources = db.query(DataSource).all()

    return sources


@router.post("/{source_code}/test", response_model=DataSourceTestResult)
async def test_source_connection(source_code: str, db: Session = Depends(get_db)):
    """Test connectivity and endpoint response for a specific data source."""
    source = db.query(DataSource).filter(DataSource.code == source_code).first()
    if not source:
        raise HTTPException(status_code=404, detail=f"Source {source_code} not found")

    start_time = time.time()
    success = False
    status_code = None
    message = ""

    if source.code == "steam_store":
        # Test Steam Web API or Storefront endpoint
        test_url = f"{source.base_url}/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=730"
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(test_url)
                status_code = res.status_code
                if res.status_code == 200:
                    success = True
                    message = "Steam API responded successfully with valid player count payload."
                else:
                    message = f"Steam API returned status {res.status_code}: {res.text[:100]}"
        except Exception as exc:
            message = f"Connection failed: {str(exc)}"
    elif source.status in ["planned", "unavailable", "disabled"]:
        message = f"Source is currently marked as '{source.status}'. No active connection test performed."
        success = False
    else:
        message = "No automated test implementation for this connector."
        success = False

    elapsed_ms = (time.time() - start_time) * 1000.0

    if success:
        source.last_verified_at = datetime.now(timezone.utc)
        db.commit()

    return DataSourceTestResult(
        provider_code=source.code,
        success=success,
        status_code=status_code,
        response_time_ms=round(elapsed_ms, 2),
        message=message,
        tested_at=datetime.now(timezone.utc)
    )
