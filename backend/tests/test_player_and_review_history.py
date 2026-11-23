import json
import os
import pytest
from app.services.catalog_sync import CatalogSyncService
from app.services.player_review_sync import PlayerReviewSyncService
from app.models.catalog import GamePlatform
from app.models.snapshots import PlayerSnapshot, ReviewSnapshot, ReviewItem


def load_fixture(filename: str):
    base_dir = os.path.dirname(__file__)
    fixture_path = os.path.join(base_dir, "fixtures", filename)
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_base_catalog(db):
    cat_service = CatalogSyncService(db=db)
    await cat_service.sync_batch(raw_payload_override=load_fixture("steam_applist.json"))


@pytest.mark.asyncio
async def test_player_snapshot_ingestion(db_session):
    """Phase 4: Test CCU player snapshots and raw payload audit."""
    await seed_base_catalog(db_session)

    cyberpunk_gp = (
        db_session.query(GamePlatform)
        .filter(GamePlatform.external_id == "1091500")
        .first()
    )
    assert cyberpunk_gp is not None

    sync_service = PlayerReviewSyncService(db=db_session)
    players_fixture = load_fixture("steam_numberofcurrentplayers.json")

    res = await sync_service.snapshot_players(
        game_id=cyberpunk_gp.game_id,
        raw_payload_override=players_fixture
    )
    assert res["success"] is True
    assert res["player_count"] == 48215
    assert res["availability_status"] == "available"

    # Verify snapshot in DB
    snap = (
        db_session.query(PlayerSnapshot)
        .filter(PlayerSnapshot.game_platform_id == cyberpunk_gp.id)
        .order_by(PlayerSnapshot.observed_at.desc())
        .first()
    )
    assert snap is not None
    assert snap.player_count == 48215
    assert snap.availability_status == "available"
    assert snap.quality_score == 100


@pytest.mark.asyncio
async def test_review_snapshot_and_items(db_session):
    """Phase 4: Test review snapshot aggregates and individual review item extraction."""
    await seed_base_catalog(db_session)

    cyberpunk_gp = (
        db_session.query(GamePlatform)
        .filter(GamePlatform.external_id == "1091500")
        .first()
    )
    assert cyberpunk_gp is not None

    sync_service = PlayerReviewSyncService(db=db_session)
    review_fixture = load_fixture("steam_reviews.json")

    res = await sync_service.sync_reviews(
        game_id=cyberpunk_gp.game_id,
        raw_payload_override=review_fixture
    )
    assert res["success"] is True
    assert res["total_reviews"] == 670000
    assert res["positive_reviews"] == 550000
    assert res["negative_reviews"] == 120000
    assert res["items_saved"] == 2

    # Verify Review Snapshot
    snap = (
        db_session.query(ReviewSnapshot)
        .filter(ReviewSnapshot.game_platform_id == cyberpunk_gp.id)
        .order_by(ReviewSnapshot.observed_at.desc())
        .first()
    )
    assert snap is not None
    assert snap.total_reviews == 670000
    assert float(snap.positive_ratio) == round(550000 / 670000, 5)

    # Verify Review Items
    items = (
        db_session.query(ReviewItem)
        .filter(ReviewItem.game_platform_id == cyberpunk_gp.id)
        .all()
    )
    assert len(items) == 2
    rec_ids = [it.source_review_id for it in items]
    assert "150000001" in rec_ids
    assert "150000002" in rec_ids


@pytest.mark.asyncio
async def test_game_history_and_watch_endpoints(client, db_session):
    """Phase 4: Test historical series retrieval and watchlist toggle."""
    await seed_base_catalog(db_session)
    cyberpunk_gp = (
        db_session.query(GamePlatform)
        .filter(GamePlatform.external_id == "1091500")
        .first()
    )
    assert cyberpunk_gp is not None
    sync_service = PlayerReviewSyncService(db=db_session)
    await sync_service.snapshot_players(
        game_id=cyberpunk_gp.game_id,
        raw_payload_override=load_fixture("steam_numberofcurrentplayers.json")
    )
    await sync_service.sync_reviews(
        game_id=cyberpunk_gp.game_id,
        raw_payload_override=load_fixture("steam_reviews.json")
    )

    game_id = str(cyberpunk_gp.game_id)

    # 1. History
    hist_resp = client.get(f"/api/v1/games/{game_id}/history")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    assert hist_data["canonical_name"] == "Cyberpunk 2077"
    assert len(hist_data["player_history"]) >= 1
    assert hist_data["player_history"][0]["player_count"] == 48215
    assert len(hist_data["review_history"]) >= 1

    # 2. Watchlist
    watch_resp = client.post(f"/api/v1/games/{game_id}/watch")
    assert watch_resp.status_code == 200
    assert watch_resp.json()["monitored"] is True

    unwatch_resp = client.delete(f"/api/v1/games/{game_id}/watch")
    assert unwatch_resp.status_code == 200
    assert unwatch_resp.json()["monitored"] is False
