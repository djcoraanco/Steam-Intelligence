import uuid
from datetime import date
import pytest
from fastapi.testclient import TestClient

from app.models.catalog import Game
from app.models.events import IndustryEvent
from app.services.seasonality import SeasonalityEngine


def test_industry_events_listing(db_session, client: TestClient, auth_headers):
    resp = client.get("/api/v1/seasonality/events", headers=auth_headers)
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) >= 5
    codes = [e["code"] for e in events]
    assert "steam_summer_sale_2026" in codes
    assert "steam_next_fest_june_2026" in codes
    assert "steam_autumn_sale_2026" in codes


def test_cohorts_analysis(db_session, client: TestClient, auth_headers):
    # Seed games across different years
    g1 = Game(id=uuid.uuid4(), canonical_name="Game 2024", release_date=date(2024, 5, 1), is_early_access=True)
    g2 = Game(id=uuid.uuid4(), canonical_name="Game 2025", release_date=date(2025, 8, 1), is_early_access=False)
    g3 = Game(id=uuid.uuid4(), canonical_name="Game 2026", release_date=date(2026, 2, 1), is_early_access=False)
    db_session.add_all([g1, g2, g3])
    db_session.commit()

    resp = client.get("/api/v1/seasonality/cohorts?dimension=release_year", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["dimension"] == "release_year"
    assert data["total_sample_size"] == 3
    cohort_names = [c["cohort"] for c in data["cohorts"]]
    assert "2024" in cohort_names
    assert "2025" in cohort_names
    assert "2026" in cohort_names
    assert "causalidad" in data["disclaimer"].lower()


def test_launch_collision_detection(db_session, client: TestClient, auth_headers):
    # Test collision with Steam Summer Sale (June 25 to July 9, 2026)
    target_summer = "2026-06-28"
    resp = client.get(f"/api/v1/seasonality/launch-collision?target_date={target_summer}&days_window=10", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["collision_score"] >= 50
    assert data["collision_level"] in ["high", "extreme"]
    assert any("Summer Sale" in ev["name"] for ev in data["overlapping_events"])
    assert len(data["alternative_windows"]) == 2
    assert "causalidad" in data["disclaimer"].lower()

    # Test clean date (e.g. May 10, 2026)
    target_clean = "2026-05-10"
    clean_resp = client.get(f"/api/v1/seasonality/launch-collision?target_date={target_clean}&days_window=7", headers=auth_headers)
    assert clean_resp.status_code == 200
    clean_data = clean_resp.json()
    assert clean_data["collision_score"] < 50
    assert clean_data["collision_level"] in ["low", "moderate"]
