from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.catalog import Game, GamePlatform, Platform
from app.schemas.games import GameListResponse, GameSummary

router = APIRouter()


@router.get("", response_model=GameListResponse)
def get_games(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Game)
    if search:
        query = query.filter(Game.canonical_name.ilike(f"%{search}%"))

    total = query.count()
    games = query.order_by(desc(Game.created_at)).offset(offset).limit(limit).all()

    items = []
    for g in games:
        gp = next((p for p in g.platforms if p.is_primary), None) or (g.platforms[0] if g.platforms else None)
        steam_appid = gp.external_id if gp else None
        items.append(
            GameSummary(
                id=g.id,
                canonical_name=g.canonical_name,
                slug=g.slug,
                release_date=g.release_date,
                release_status=g.release_status,
                game_type=g.game_type,
                is_early_access=g.is_early_access,
                cover_image_url=g.cover_image_url,
                steam_appid=steam_appid,
                last_seen_at=gp.last_seen_at if gp else None
            )
        )

    return GameListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{game_id}", response_model=GameSummary)
def get_game(game_id: uuid.UUID, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    gp = next((p for p in game.platforms if p.is_primary), None) or (game.platforms[0] if game.platforms else None)
    return GameSummary(
        id=game.id,
        canonical_name=game.canonical_name,
        slug=game.slug,
        release_date=game.release_date,
        release_status=game.release_status,
        game_type=game.game_type,
        is_early_access=game.is_early_access,
        cover_image_url=game.cover_image_url,
        steam_appid=gp.external_id if gp else None,
        last_seen_at=gp.last_seen_at if gp else None
    )
