from typing import Optional, List
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.catalog import (
    Game, GamePlatform, Organization, GameDeveloper, GamePublisher,
    TaxonomyItem, GameTaxonomy
)
from app.models.snapshots import PriceSnapshot, PlayerSnapshot
from app.schemas.games import GameListResponse, GameSummary, GameDetailResponse
from app.services.metadata_sync import MetadataSyncService

router = APIRouter()


@router.get("", response_model=GameListResponse)
def get_games(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    game_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Game)
    if search:
        query = query.filter(Game.canonical_name.ilike(f"%{search}%"))
    if game_type:
        query = query.filter(Game.game_type == game_type)

    total = query.count()
    games = query.order_by(desc(Game.created_at)).offset(offset).limit(limit).all()

    items = []
    for g in games:
        gp = next((p for p in g.platforms if p.is_primary), None) or (g.platforms[0] if g.platforms else None)
        steam_appid = gp.external_id if gp else None
        store_url = gp.store_url if gp else None

        # Price snapshot
        price_snap = None
        if gp:
            price_snap = (
                db.query(PriceSnapshot)
                .filter(PriceSnapshot.game_platform_id == gp.id)
                .order_by(desc(PriceSnapshot.observed_at))
                .first()
            )

        items.append(
            GameSummary(
                id=g.id,
                canonical_name=g.canonical_name,
                slug=g.slug,
                release_date=g.release_date,
                release_date_precision=g.release_date_precision,
                release_status=g.release_status,
                game_type=g.game_type,
                is_early_access=g.is_early_access,
                cover_image_url=g.cover_image_url,
                steam_appid=steam_appid,
                store_url=store_url,
                price_cents=price_snap.final_price_minor if price_snap else None,
                currency=price_snap.currency if price_snap else "USD",
                is_free=price_snap.is_free if price_snap else False,
                availability_status=price_snap.availability_status if price_snap else "available",
                last_seen_at=gp.last_seen_at if gp else None
            )
        )

    return GameListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{game_id}", response_model=GameDetailResponse)
def get_game(game_id: uuid.UUID, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    gp = next((p for p in game.platforms if p.is_primary), None) or (game.platforms[0] if game.platforms else None)
    steam_appid = gp.external_id if gp else None
    store_url = gp.store_url if gp else None

    # Fetch latest price
    price_snap = None
    if gp:
        price_snap = (
            db.query(PriceSnapshot)
            .filter(PriceSnapshot.game_platform_id == gp.id)
            .order_by(desc(PriceSnapshot.observed_at))
            .first()
        )

    # Fetch developers
    dev_links = db.query(GameDeveloper).filter(GameDeveloper.game_id == game.id).all()
    dev_ids = [d.organization_id for d in dev_links]
    developers = [org.canonical_name for org in db.query(Organization).filter(Organization.id.in_(dev_ids)).all()] if dev_ids else []

    # Fetch publishers
    pub_links = db.query(GamePublisher).filter(GamePublisher.game_id == game.id).all()
    pub_ids = [p.organization_id for p in pub_links]
    publishers = [org.canonical_name for org in db.query(Organization).filter(Organization.id.in_(pub_ids)).all()] if pub_ids else []

    # Fetch genres
    tax_links = db.query(GameTaxonomy).filter(GameTaxonomy.game_id == game.id).all()
    tax_ids = [t.taxonomy_id for t in tax_links]
    genres = [item.canonical_name for item in db.query(TaxonomyItem).filter(TaxonomyItem.id.in_(tax_ids)).all()] if tax_ids else []

    return GameDetailResponse(
        id=game.id,
        canonical_name=game.canonical_name,
        slug=game.slug,
        description=game.description,
        short_description=game.short_description,
        release_date=game.release_date,
        release_date_precision=game.release_date_precision or "unknown",
        release_status=game.release_status,
        game_type=game.game_type,
        is_early_access=game.is_early_access,
        cover_image_url=game.cover_image_url,
        website_url=game.website_url,
        steam_appid=steam_appid,
        store_url=store_url,
        regular_price_cents=price_snap.regular_price_minor if price_snap else None,
        final_price_cents=price_snap.final_price_minor if price_snap else None,
        discount_percent=float(price_snap.discount_percent) if (price_snap and price_snap.discount_percent is not None) else None,
        currency=price_snap.currency if price_snap else "USD",
        is_free=price_snap.is_free if price_snap else False,
        price_status=price_snap.availability_status if price_snap else "available",
        developers=developers,
        publishers=publishers,
        genres=genres,
        created_at=game.created_at,
        updated_at=game.updated_at
    )


@router.post("/{game_id}/sync-metadata")
async def sync_game_metadata_endpoint(game_id: uuid.UUID, db: Session = Depends(get_db)):
    """Trigger on-demand metadata & storefront synchronization for a specific game."""
    service = MetadataSyncService(db=db)
    try:
        result = await service.sync_game_details(game_id=game_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storefront sync failed: {str(e)}")
