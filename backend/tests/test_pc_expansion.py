import uuid
from datetime import date
import pytest
from fastapi.testclient import TestClient

from app.models.catalog import Game
from app.services.pc_expansion import CrossPlatformService, IGDBConnector, ItchConnector


def test_pc_expansion_store_registry(client: TestClient, auth_headers):
    resp = client.get("/api/v1/cross-platform/stores", headers=auth_headers)
    assert resp.status_code == 200
    registry = resp.json()

    assert "igdb" in registry
    assert "itch_io" in registry
    assert "gog" in registry
    assert "epic_games" in registry

    assert registry["igdb"]["attribution_required"] is True
    assert "IGDB" in registry["igdb"]["attribution_notice"]
    assert registry["gog"]["status"] == "metadata_only"
    assert registry["epic_games"]["status"] == "metadata_only"


def test_cross_platform_game_link(db_session, client: TestClient, auth_headers):
    g = Game(id=uuid.uuid4(), canonical_name="Hollow Knight", release_date=date(2017, 2, 24))
    db_session.add(g)
    db_session.commit()

    # Link to IGDB
    resp = client.post(
        "/api/v1/cross-platform/link",
        headers=auth_headers,
        json={
            "game_id": str(g.id),
            "platform_code": "igdb",
            "external_id": "1942",
            "external_title": "Hollow Knight",
            "store_url": "https://www.igdb.com/games/hollow-knight",
            "match_confidence": "verified",
            "match_method": "steam_appid_link",
            "metadata": {"rating": 91.5, "franchise": "Hollow Knight"}
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["match_confidence"] == "verified"

    # Query cross references
    get_resp = client.get(f"/api/v1/cross-platform/{g.id}", headers=auth_headers)
    assert get_resp.status_code == 200
    refs = get_resp.json()
    assert len(refs) == 1
    assert refs[0]["platform_code"] == "igdb"
    assert "IGDB" in refs[0]["attribution_notice"]
    assert refs[0]["metadata"]["rating"] == 91.5


def test_itch_rss_parser():
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>itch.io new games</title>
        <item>
          <title>Pixel Dungeon Quest</title>
          <link>https://creator.itch.io/pixel-dungeon</link>
          <description>A retro 2D rogue-like dungeon crawler.</description>
          <pubDate>Mon, 23 Nov 2026 12:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """
    connector = ItchConnector()
    items = connector.parse_rss_feed(sample_xml)
    assert len(items) == 1
    assert items[0]["title"] == "Pixel Dungeon Quest"
    assert items[0]["data_class"] == "public_discovery_data"
    assert items[0]["source"] == "itch_io_public_feed"


@pytest.mark.asyncio
async def test_igdb_connector():
    connector = IGDBConnector()
    token = await connector.authenticate()
    assert token is not None
    headers = connector.get_headers()
    assert "Client-ID" in headers
    assert "Authorization" in headers
    assert "IGDB" in connector.format_attribution()
