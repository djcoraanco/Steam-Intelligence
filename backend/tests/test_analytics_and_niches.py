import json
import os
import pytest
from app.services.catalog_sync import CatalogSyncService
from app.services.metadata_sync import MetadataSyncService
from app.services.player_review_sync import PlayerReviewSyncService
from app.services.analytics_engine import AnalyticsEngine, calculate_growth_rate
from app.services.niche_finder import NicheFinderService
from app.models.catalog import Game, GamePlatform, TaxonomyItem, GameTaxonomy
from app.models.snapshots import PlayerSnapshot, PriceSnapshot
from app.models.rollups import GameMetricRollup, MarketSegmentRollup
from app.models.research import NicheOpportunity


def load_fixture(filename: str):
    base_dir = os.path.dirname(__file__)
    fixture_path = os.path.join(base_dir, "fixtures", filename)
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_analytics_data(db):
    cat_service = CatalogSyncService(db=db)
    await cat_service.sync_batch(raw_payload_override=load_fixture("steam_applist.json"))

    cyberpunk_gp = (
        db.query(GamePlatform)
        .filter(GamePlatform.external_id == "1091500")
        .first()
    )
    if cyberpunk_gp:
        meta_service = MetadataSyncService(db=db)
        await meta_service.sync_game_details(
            game_id=cyberpunk_gp.game_id,
            raw_payload_override=load_fixture("steam_appdetails_success.json")
        )
        pr_service = PlayerReviewSyncService(db=db)
        await pr_service.snapshot_players(
            game_id=cyberpunk_gp.game_id,
            raw_payload_override=load_fixture("steam_numberofcurrentplayers.json")
        )
        await pr_service.sync_reviews(
            game_id=cyberpunk_gp.game_id,
            raw_payload_override=load_fixture("steam_reviews.json")
        )


def test_growth_rate_deterministic_rules():
    """Phase 5: Test growth calculation with zero, missing, and valid baselines."""
    # 1. Normal growth
    assert calculate_growth_rate(current=150.0, baseline=100.0) == 50.0
    assert calculate_growth_rate(current=80.0, baseline=100.0) == -20.0

    # 2. Baseline is zero: Must return None (never infinity / ZeroDivisionError)
    assert calculate_growth_rate(current=100.0, baseline=0.0) is None

    # 3. Baseline is negative or None
    assert calculate_growth_rate(current=100.0, baseline=-5.0) is None
    assert calculate_growth_rate(current=100.0, baseline=None) is None
    assert calculate_growth_rate(current=None, baseline=100.0) is None


@pytest.mark.asyncio
async def test_game_and_segment_rollups(db_session):
    """Phase 5: Test deterministic rollups computation."""
    await seed_analytics_data(db_session)

    cyberpunk_gp = (
        db_session.query(GamePlatform)
        .filter(GamePlatform.external_id == "1091500")
        .first()
    )
    assert cyberpunk_gp is not None

    engine = AnalyticsEngine(db=db_session)

    # 1. Game rollup
    rollup = engine.compute_game_rollups(game_platform_id=cyberpunk_gp.id, period_type="day")
    assert rollup is not None
    assert rollup.max_players == 48215
    assert rollup.calculation_version == "analytics-v1"

    # 2. Segment rollups
    segment_rollups = engine.compute_all_market_segment_rollups(period_type="day")
    assert len(segment_rollups) >= 1
    action_rollup = next((r for r in segment_rollups if r.segment_key.get("canonical_name") == "Action"), None)
    assert action_rollup is not None
    assert action_rollup.game_count >= 1
    assert action_rollup.top_game_concentration is not None


@pytest.mark.asyncio
async def test_niche_finder_algorithm_and_explainability(db_session):
    """Phase 6: Test official Opportunity formula weights, breakdown, and empty protection."""
    await seed_analytics_data(db_session)
    service = NicheFinderService(db=db_session)

    # 1. Empty segment test -> must return insufficient_data without fabricating scores
    empty_res = service.calculate_niche_score("NonExistentGenre", [])
    assert empty_res["status"] == "insufficient_data"
    assert empty_res["opportunity_score"] == 0.0
    assert empty_res["confidence_band"] == "low"
    assert len(empty_res["limitations"]) > 0

    # 2. Real segment calculation
    action_genre = db_session.query(TaxonomyItem).filter(TaxonomyItem.canonical_name == "Action").first()
    assert action_genre is not None

    tax_links = db_session.query(GameTaxonomy).filter(GameTaxonomy.taxonomy_id == action_genre.id).all()
    game_ids = [tl.game_id for tl in tax_links]
    assert len(game_ids) > 0

    score_res = service.calculate_niche_score("Action", game_ids)
    assert score_res["status"] == "calculated"
    assert 0.0 <= score_res["demand_score"] <= 100.0
    assert 0.0 <= score_res["growth_score"] <= 100.0
    assert 0.0 <= score_res["competitive_space_score"] <= 100.0
    assert 0.0 <= score_res["commercial_feasibility_score"] <= 100.0
    assert 0.0 <= score_res["evidence_quality_score"] <= 100.0
    assert 0.0 <= score_res["opportunity_score"] <= 100.0

    # Verify formula weights: 0.30*Demand + 0.25*Growth + 0.20*CompetitiveSpace + 0.15*CommercialFeasibility + 0.10*EvidenceQuality
    expected_opp = round(
        0.30 * score_res["demand_score"] +
        0.25 * score_res["growth_score"] +
        0.20 * score_res["competitive_space_score"] +
        0.15 * score_res["commercial_feasibility_score"] +
        0.10 * score_res["evidence_quality_score"],
        2
    )
    assert score_res["opportunity_score"] == expected_opp

    # 3. Analyze and record all niches
    recorded_niches = service.analyze_and_record_all_niches()
    assert len(recorded_niches) >= 1
    saved_action = db_session.query(NicheOpportunity).filter(NicheOpportunity.name == "Action").first()
    assert saved_action is not None
    assert saved_action.score_version == "niche-v1"


@pytest.mark.asyncio
async def test_analytics_and_niches_api(client, db_session):
    """Test API endpoints for analytics rollups and niche opportunities."""
    await seed_analytics_data(db_session)
    engine = AnalyticsEngine(db=db_session)
    engine.compute_all_market_segment_rollups(period_type="day")

    niche_service = NicheFinderService(db=db_session)
    niche_service.analyze_and_record_all_niches()

    # 1. Analytics segments
    seg_resp = client.get("/api/v1/analytics/segments?segment_type=genre")
    assert seg_resp.status_code == 200
    seg_data = seg_resp.json()
    assert len(seg_data) >= 1

    # 2. Niches listing
    niche_resp = client.get("/api/v1/niches")
    assert niche_resp.status_code == 200
    niche_data = niche_resp.json()
    assert len(niche_data) >= 1
    assert "opportunity_score" in niche_data[0]
    assert "confidence_band" in niche_data[0]
    assert "demand_score" in niche_data[0]

    # 3. Niche analyze POST
    analyze_resp = client.post("/api/v1/niches/analyze")
    assert analyze_resp.status_code == 200
    assert analyze_resp.json()["analyzed_niches_count"] >= 1
