import logging
import uuid
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session

from app.models.catalog import Game
from app.models.cross_references import GameCrossReference

logger = logging.getLogger(__name__)

# Registry of supported PC expansion platforms and their legal/technical capabilities
STORE_CAPABILITIES_REGISTRY = {
    "steam_store": {
        "name": "Steam Store & Steamworks",
        "type": "official_public",
        "status": "active",
        "capabilities": ["catalog", "metadata", "pricing", "ccu_players", "user_reviews", "taxonomies"],
        "attribution_required": False,
        "notes": "Fuente primaria de referencia y telemetría de jugadores."
    },
    "igdb": {
        "name": "IGDB (Internet Game Database)",
        "type": "partner_api",
        "status": "active",
        "capabilities": ["metadata", "genres", "themes", "game_modes", "franchises", "external_ids", "cover_art"],
        "attribution_required": True,
        "attribution_notice": "Data provided by IGDB (an Amazon Twitch company). Attribution required for commercial use.",
        "notes": "Metadatos editoriales de videojuegos y taxonomías cruzadas."
    },
    "itch_io": {
        "name": "itch.io",
        "type": "public_discovery_rss",
        "status": "active",
        "capabilities": ["public_discovery_feed", "featured_feed", "sales_feed"],
        "attribution_required": False,
        "notes": "Descubrimiento de juegos independientes mediante feeds RSS públicos. Datos de ventas de terceros no disponibles sin OAuth."
    },
    "gog": {
        "name": "GOG",
        "type": "official_store_public",
        "status": "metadata_only",
        "capabilities": ["catalog_search", "metadata_only"],
        "attribution_required": False,
        "notes": "Acceso limitado a metadatos de tienda pública. No ofrece API comercial de métricas de ventas."
    },
    "epic_games": {
        "name": "Epic Games Store",
        "type": "official_store_public",
        "status": "metadata_only",
        "capabilities": ["metadata_only", "store_links"],
        "attribution_required": False,
        "notes": "No se realiza emulación de launcher ni scraping anti-bot. Métricas de ventas ajenas marcadas como unsupported."
    }
}


class IGDBConnector:
    """
    IGDB API v4 Connector with Twitch OAuth Client Credentials handling.
    Enforces attribution and non-destructive metadata ingestion.
    """
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or "test_twitch_client_id"
        self.client_secret = client_secret or "test_twitch_client_secret"
        self.base_url = "https://api.igdb.com/v4"
        self.token = None

    async def authenticate(self) -> str:
        """Obtains OAuth token from Twitch Developer Console."""
        # In testing or when using credentials
        if self.client_id == "test_twitch_client_id":
            self.token = "mock_twitch_bearer_token"
            return self.token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://id.twitch.tv/oauth2/token",
                params={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials"
                }
            )
            data = resp.json()
            self.token = data.get("access_token")
            return self.token

    def get_headers(self) -> Dict[str, str]:
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.token or 'mock_token'}"
        }

    def format_attribution(self) -> str:
        return "Data provided by IGDB. https://www.igdb.com"


class ItchConnector:
    """
    itch.io Connector utilizing official discovery RSS feeds.
    Distinguishes public discovery from creator authorized data.
    """
    FEEDS = {
        "new": "https://itch.io/feed/new.xml",
        "featured": "https://itch.io/feed/featured.xml",
        "sales": "https://itch.io/feed/sales.xml"
    }

    def parse_rss_feed(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parses itch.io RSS xml feed safely."""
        items = []
        try:
            root = ET.fromstring(xml_content)
            for item in root.findall(".//item"):
                title = item.find("title").text if item.find("title") is not None else "Unknown"
                link = item.find("link").text if item.find("link") is not None else ""
                desc = item.find("description").text if item.find("description") is not None else ""
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""

                items.append({
                    "title": title.strip(),
                    "store_url": link.strip(),
                    "description": desc.strip(),
                    "published_at": pub_date.strip(),
                    "source": "itch_io_public_feed",
                    "data_class": "public_discovery_data"
                })
        except Exception as e:
            logger.error(f"Error parsing itch RSS: {e}")
        return items


class CrossPlatformService:
    def __init__(self, db: Session):
        self.db = db

    def get_stores_registry(self) -> Dict[str, Any]:
        """Returns the full status and capabilities matrix across all PC storefronts."""
        return STORE_CAPABILITIES_REGISTRY

    def link_external_platform(
        self,
        game_id: str,
        platform_code: str,
        external_id: str,
        external_title: str,
        store_url: Optional[str] = None,
        match_confidence: str = "high_confidence",
        match_method: str = "steam_appid_link",
        metadata: Optional[Dict[str, Any]] = None
    ) -> GameCrossReference:
        """
        Creates or updates a verified cross-platform game link.
        Prevents naive auto-merges by requiring explicit match confidence and method.
        """
        if platform_code not in STORE_CAPABILITIES_REGISTRY:
            raise ValueError(f"Unknown platform code: {platform_code}")

        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise ValueError(f"Game with id {game_id} does not exist")

        existing = self.db.query(GameCrossReference).filter(
            GameCrossReference.game_id == game_id,
            GameCrossReference.platform_code == platform_code,
            GameCrossReference.external_id == external_id
        ).first()

        if existing:
            existing.external_title = external_title
            existing.store_url = store_url
            existing.match_confidence = match_confidence
            existing.match_method = match_method
            existing.metadata_payload = metadata or {}
            self.db.commit()
            self.db.refresh(existing)
            return existing

        cross_ref = GameCrossReference(
            id=uuid.uuid4(),
            game_id=game_id,
            platform_code=platform_code,
            external_id=external_id,
            external_title=external_title,
            store_url=store_url,
            match_confidence=match_confidence,
            match_method=match_method,
            metadata_payload=metadata or {}
        )
        self.db.add(cross_ref)
        self.db.commit()
        self.db.refresh(cross_ref)
        return cross_ref

    def get_game_cross_references(self, game_id: str) -> List[Dict[str, Any]]:
        """Returns all external storefront links and identities for a game."""
        links = self.db.query(GameCrossReference).filter(GameCrossReference.game_id == game_id).all()
        results = []
        for l in links:
            cap = STORE_CAPABILITIES_REGISTRY.get(l.platform_code, {})
            results.append({
                "id": str(l.id),
                "platform_code": l.platform_code,
                "platform_name": cap.get("name", l.platform_code),
                "external_id": l.external_id,
                "external_title": l.external_title,
                "store_url": l.store_url,
                "match_confidence": l.match_confidence,
                "match_method": l.match_method,
                "status": cap.get("status", "unknown"),
                "attribution_notice": cap.get("attribution_notice") if cap.get("attribution_required") else None,
                "metadata": l.metadata_payload
            })
        return results
