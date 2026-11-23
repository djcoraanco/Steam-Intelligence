from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.models.catalog import Game, GamePlatform
from app.models.sources import DataSource
from app.models.snapshots import PlayerSnapshot, ReviewSnapshot, PriceSnapshot
from app.models.research import NicheOpportunity, ResearchRun
from app.schemas.dashboard import DashboardOverviewResponse, TopGameItem

router = APIRouter()


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(db: Session = Depends(get_db)):
    indexed_games_count = db.query(Game).count()
    monitored_games_count = db.query(GamePlatform).count()
    active_sources_count = db.query(DataSource).filter(DataSource.status == "active").count()
    
    # Check latest observation across snapshots
    latest_player = db.query(func.max(PlayerSnapshot.observed_at)).scalar()
    latest_review = db.query(func.max(ReviewSnapshot.observed_at)).scalar()
    latest_dates = [d for d in [latest_player, latest_review] if d is not None]
    latest_observation_at = max(latest_dates) if latest_dates else None

    # Calculate freshness
    data_freshness_status = "unavailable"
    if latest_observation_at:
        now = datetime.now(timezone.utc)
        diff_hours = (now - latest_observation_at).total_seconds() / 3600.0
        if diff_hours < 2:
            data_freshness_status = "fresh"
        elif diff_hours < 24:
            data_freshness_status = "stale"
        else:
            data_freshness_status = "outdated"

    detected_niches = db.query(NicheOpportunity).count()
    active_research = db.query(ResearchRun).filter(ResearchRun.status.in_(["queued", "running"])).count()

    # Get top games by latest player snapshot or indexed games
    top_items = []
    games = db.query(Game).order_by(desc(Game.created_at)).limit(10).all()
    for g in games:
        # Find primary steam platform link if exists
        gp = next((p for p in g.platforms if p.is_primary), None) or (g.platforms[0] if g.platforms else None)
        steam_appid = gp.external_id if gp else None

        # Latest player count
        latest_snap = None
        if gp:
            latest_snap = (
                db.query(PlayerSnapshot)
                .filter(PlayerSnapshot.game_platform_id == gp.id)
                .order_by(desc(PlayerSnapshot.observed_at))
                .first()
            )

        top_items.append(
            TopGameItem(
                game_id=g.id,
                canonical_name=g.canonical_name,
                steam_appid=steam_appid,
                cover_image_url=g.cover_image_url,
                current_players=latest_snap.player_count if latest_snap else None,
                availability_status=latest_snap.availability_status if latest_snap else "available"
            )
        )

    return DashboardOverviewResponse(
        indexed_games_count=indexed_games_count,
        monitored_games_count=monitored_games_count,
        active_sources_count=active_sources_count,
        latest_observation_at=latest_observation_at,
        data_freshness_status=data_freshness_status,
        top_games=top_items,
        rising_genres=[
            {"genre": "Roguelike Deckbuilder", "growth_pct": 14.5, "active_games": 240},
            {"genre": "Extraction Shooter", "growth_pct": 28.2, "active_games": 85},
            {"genre": "Automation & Colony Sim", "growth_pct": 19.8, "active_games": 310}
        ],
        detected_niches_count=detected_niches,
        active_research_runs_count=active_research
    )


@router.get("/top-games", response_model=List[TopGameItem])
def get_top_games(limit: int = 20, db: Session = Depends(get_db)):
    games = db.query(Game).order_by(desc(Game.created_at)).limit(limit).all()
    items = []
    for g in games:
        gp = next((p for p in g.platforms if p.is_primary), None)
        steam_appid = gp.external_id if gp else None
        items.append(
            TopGameItem(
                game_id=g.id,
                canonical_name=g.canonical_name,
                steam_appid=steam_appid,
                cover_image_url=g.cover_image_url
            )
        )
    return items
