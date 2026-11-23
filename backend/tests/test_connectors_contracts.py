import json
import os
import pytest
from app.connectors.registry import CONNECTORS_METADATA, get_connector_metadata
from app.connectors.steam import SteamConnector


def load_fixture(filename: str):
    base_dir = os.path.dirname(__file__)
    fixture_path = os.path.join(base_dir, "fixtures", filename)
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_connectors_registry():
    """Verify registry conforms to Section 3.9 of the Master Specification."""
    steam_meta = get_connector_metadata("steam_store")
    assert steam_meta["provider_code"] == "steam_store"
    assert steam_meta["status"] == "active"
    assert "catalog" in steam_meta["capabilities"]
    assert "current_players" in steam_meta["capabilities"]
    assert "reviews" in steam_meta["capabilities"]

    # Verify all declared connectors have required fields
    for meta in CONNECTORS_METADATA:
        assert "provider_code" in meta
        assert "provider_name" in meta
        assert "provider_type" in meta
        assert "status" in meta
        assert "capabilities" in meta
        assert "terms_url" in meta
        assert "rate_limit_policy" in meta


def test_steam_applist_contract():
    fixture = load_fixture("steam_applist.json")
    assert "response" in fixture
    assert "apps" in fixture["response"]
    apps = fixture["response"]["apps"]
    assert len(apps) >= 3
    assert apps[0]["appid"] == 730
    assert apps[0]["name"] == "Counter-Strike 2"
    assert fixture["response"]["have_more_results"] is True
    assert fixture["response"]["last_appid"] == 1091500


def test_steam_appdetails_success_contract():
    fixture = load_fixture("steam_appdetails_success.json")
    appid_str = "1091500"
    assert appid_str in fixture
    app_data = fixture[appid_str]
    assert app_data["success"] is True

    details = app_data["data"]
    assert details["name"] == "Cyberpunk 2077"
    assert details["steam_appid"] == 1091500
    assert details["is_free"] is False
    assert details["price_overview"]["currency"] == "USD"
    # Currency in minor units (cents): 2999 = $29.99
    assert details["price_overview"]["final"] == 2999
    assert details["price_overview"]["discount_percent"] == 50
    assert len(details["developers"]) > 0
    assert len(details["genres"]) > 0


def test_steam_appdetails_empty_contract():
    fixture = load_fixture("steam_appdetails_empty.json")
    appid_str = "999999999"
    assert appid_str in fixture
    assert fixture[appid_str]["success"] is False


def test_steam_numberofcurrentplayers_contract():
    fixture = load_fixture("steam_numberofcurrentplayers.json")
    assert "response" in fixture
    assert fixture["response"]["player_count"] == 48215
    assert fixture["response"]["result"] == 1


def test_steam_reviews_contract():
    fixture = load_fixture("steam_reviews.json")
    assert fixture["success"] == 1
    assert "query_summary" in fixture
    summary = fixture["query_summary"]
    assert summary["total_reviews"] == 670000
    assert summary["total_positive"] == 550000
    assert summary["total_negative"] == 120000
    # Positive ratio calculation
    ratio = summary["total_positive"] / summary["total_reviews"]
    assert round(ratio, 4) == round(550000 / 670000, 4)

    assert "reviews" in fixture
    assert len(fixture["reviews"]) == 2
    assert fixture["reviews"][0]["voted_up"] is True
    assert fixture["reviews"][1]["voted_up"] is False
    assert "cursor" in fixture
