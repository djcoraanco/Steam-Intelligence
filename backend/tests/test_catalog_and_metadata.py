import json
import os
import pytest
from app.services.catalog_sync import CatalogSyncService
from app.services.metadata_sync import MetadataSyncService
from app.models.catalog import Game, GamePlatform, Platform, Organization, TaxonomyItem
from app.models.snapshots import PriceSnapshot
from app.models.sources import RawPayload
from app.models.checkpoints import IngestionCheckpoint


def load_fixture(filename: str):
    base_dir = os.path.dirname(__file__)
    fixture_path = os.path.join(base_dir, "fixtures", filename)
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_base_catalog(db):
    cat_service = CatalogSyncService(db=db)
    await cat_service.sync_batch(raw_payload_override=load_fixture("steam_applist.json"))


@pytest.mark.asyncio
async def test_catalog_sync_batch_and_checkpointing(db_session):
    """Phase 2: Test catalog ingestion, platform linking, raw payload hashing and checkpointing."""
    fixture = load_fixture("steam_applist.json")
    service = CatalogSyncService(db=db_session)

    result = await service.sync_batch(raw_payload_override=fixture)
    assert result["success"] is True
    assert result["imported"] == 3
    assert result["have_more_results"] is True
    assert result["last_appid"] == 1091500

    # Verify platform was created
    platform = db_session.query(Platform).filter(Platform.code == "steam").first()
    assert platform is not None
    assert platform.name == "Steam"

    # Verify games were created
    games = db_session.query(Game).all()
    assert len(games) >= 3
    game_names = [g.canonical_name for g in games]
    assert "Counter-Strike 2" in game_names
    assert "Cyberpunk 2077" in game_names

    # Verify game_platforms mapping
    cyberpunk_gp = (
        db_session.query(GamePlatform)
        .filter(GamePlatform.external_id == "1091500")
        .first()
    )
    assert cyberpunk_gp is not None
    assert cyberpunk_gp.store_url == "https://store.steampowered.com/app/1091500/"

    # Verify raw payload was stored with SHA-256 hash
    raw_payload = (
        db_session.query(RawPayload)
        .filter(RawPayload.parser_version == "catalog-v1")
        .order_by(RawPayload.fetched_at.desc())
        .first()
    )
    assert raw_payload is not None
    assert len(raw_payload.payload_hash) == 64

    # Verify checkpoint
    checkpoint = service.get_or_create_checkpoint()
    assert checkpoint.last_cursor == "1091500"
    assert checkpoint.status == "in_progress"
    assert checkpoint.total_records >= 3


@pytest.mark.asyncio
async def test_catalog_deduplication(db_session):
    """Phase 2: Running sync again must not duplicate games or game_platforms."""
    fixture = load_fixture("steam_applist.json")
    service = CatalogSyncService(db=db_session)

    # First run
    await service.sync_batch(raw_payload_override=fixture)
    initial_games_count = db_session.query(Game).count()
    initial_gp_count = db_session.query(GamePlatform).count()

    # Second run with same fixture
    result = await service.sync_batch(raw_payload_override=fixture)
    assert result["success"] is True
    assert result["imported"] == 0
    assert result["updated"] == 3

    assert db_session.query(Game).count() == initial_games_count
    assert db_session.query(GamePlatform).count() == initial_gp_count


@pytest.mark.asyncio
async def test_metadata_sync_success(db_session):
    """Phase 3: Test appdetails ingestion, price in cents, organizations, and taxonomies."""
    await seed_base_catalog(db_session)
    fixture = load_fixture("steam_appdetails_success.json")
    meta_service = MetadataSyncService(db=db_session)

    # Find Cyberpunk game
    cyberpunk_gp = (
        db_session.query(GamePlatform)
        .filter(GamePlatform.external_id == "1091500")
        .first()
    )
    assert cyberpunk_gp is not None

    result = await meta_service.sync_game_details(
        game_id=cyberpunk_gp.game_id,
        raw_payload_override=fixture
    )
    assert result["success"] is True
    assert result["appid"] == 1091500
    assert result["has_price"] is True

    # Verify Game attributes updated
    game = db_session.query(Game).filter(Game.id == cyberpunk_gp.game_id).first()
    assert "Night City" in game.short_description
    assert game.cover_image_url is not None
    assert game.release_date is not None
    assert game.release_status == "released"

    # Verify Price Snapshot in cents (minor units)
    price_snap = (
        db_session.query(PriceSnapshot)
        .filter(PriceSnapshot.game_platform_id == cyberpunk_gp.id)
        .first()
    )
    assert price_snap is not None
    assert price_snap.final_price_minor == 2999  # $29.99 in cents
    assert price_snap.regular_price_minor == 5999  # $59.99 in cents
    assert float(price_snap.discount_percent) == 50.0
    assert price_snap.currency == "USD"
    assert price_snap.availability_status == "available"

    # Verify Developer & Publisher
    org = db_session.query(Organization).filter(Organization.canonical_name == "CD PROJEKT RED").first()
    assert org is not None

    # Verify Genres
    action_genre = db_session.query(TaxonomyItem).filter(TaxonomyItem.canonical_name == "Action").first()
    assert action_genre is not None


@pytest.mark.asyncio
async def test_metadata_sync_graceful_degradation(db_session):
    """Phase 3: If appdetails returns success=false, do NOT crash, and do NOT invent zero price."""
    await seed_base_catalog(db_session)
    meta_service = MetadataSyncService(db=db_session)

    # Find CS2
    cs2_gp = (
        db_session.query(GamePlatform)
        .filter(GamePlatform.external_id == "730")
        .first()
    )
    assert cs2_gp is not None

    # Sync using empty fixture (success=false)
    result = await meta_service.sync_game_details(
        game_id=cs2_gp.game_id,
        raw_payload_override={"730": {"success": False}}
    )
    assert result["success"] is False
    assert result["availability_status"] == "unavailable"

    # Verify price snapshot was created as unavailable, NOT zero
    price_snap = (
        db_session.query(PriceSnapshot)
        .filter(PriceSnapshot.game_platform_id == cs2_gp.id)
        .first()
    )
    assert price_snap is not None
    assert price_snap.availability_status == "unavailable"
    assert price_snap.final_price_minor is None  # NOT 0!


@pytest.mark.asyncio
async def test_api_catalog_and_games(client, db_session):
    """Test API endpoints for catalog status and games detail."""
    await seed_base_catalog(db_session)
    meta_service = MetadataSyncService(db=db_session)
    cyberpunk_gp = (
        db_session.query(GamePlatform)
        .filter(GamePlatform.external_id == "1091500")
        .first()
    )
    await meta_service.sync_game_details(
        game_id=cyberpunk_gp.game_id,
        raw_payload_override=load_fixture("steam_appdetails_success.json")
    )

    # 1. Catalog status
    stat_resp = client.get("/api/v1/catalog/status")
    assert stat_resp.status_code == 200
    stat_data = stat_resp.json()
    assert stat_data["provider_code"] == "steam_store"
    assert stat_data["total_records"] >= 3

    # 2. Games list
    games_resp = client.get("/api/v1/games?limit=10")
    assert games_resp.status_code == 200
    games_data = games_resp.json()
    assert games_data["total"] >= 3
    assert len(games_data["items"]) >= 3

    cyberpunk_item = next(item for item in games_data["items"] if item["canonical_name"] == "Cyberpunk 2077")
    assert cyberpunk_item["steam_appid"] == "1091500"
    assert cyberpunk_item["price_cents"] == 2999

    # 3. Game detail endpoint
    game_id = cyberpunk_item["id"]
    detail_resp = client.get(f"/api/v1/games/{game_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["canonical_name"] == "Cyberpunk 2077"
    assert "CD PROJEKT RED" in detail_data["developers"]
    assert "Action" in detail_data["genres"]
    assert detail_data["final_price_cents"] == 2999
    assert detail_data["regular_price_cents"] == 5999
    assert detail_data["discount_percent"] == 50.0
