import hashlib
import json
import uuid
import re
from datetime import datetime, timezone, date
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.connectors.steam import SteamConnector
from app.models.catalog import (
    Game, GamePlatform, Organization, GameDeveloper, GamePublisher,
    TaxonomyItem, GameTaxonomy
)
from app.models.sources import DataSource, RawPayload
from app.models.snapshots import PriceSnapshot
from app.core.logging import logger


def now_utc():
    return datetime.now(timezone.utc)


def parse_steam_date(date_str: Optional[str]) -> Optional[date]:
    if not date_str:
        return None
    date_str = date_str.strip()
    # Try parsing "10 Dec, 2020" or "Dec 10, 2020"
    for fmt in ("%d %b, %Y", "%b %d, %Y", "%d %B, %Y", "%B %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    # Try matching year e.g. "2020"
    year_match = re.search(r"\b(19\d\d|20\d\d)\b", date_str)
    if year_match:
        try:
            return date(int(year_match.group(1)), 1, 1)
        except ValueError:
            pass
    return None


class MetadataSyncService:
    def __init__(self, db: Session, connector: Optional[SteamConnector] = None):
        self.db = db
        self.connector = connector or SteamConnector()

    def _ensure_steam_source(self) -> DataSource:
        source = self.db.query(DataSource).filter(DataSource.code == "steam_store").first()
        if not source:
            source = DataSource(
                id=uuid.uuid4(),
                code="steam_store",
                name="Steam Store & Steamworks",
                provider_type="official_public",
                base_url="https://api.steampowered.com",
                status="active",
                capabilities=["catalog", "metadata", "prices", "genres", "tags", "screenshots", "current_players", "reviews"],
                created_at=now_utc()
            )
            self.db.add(source)
            self.db.flush()
        return source

    async def sync_game_details(
        self,
        game_id: uuid.UUID,
        country_code: str = "us",
        language: str = "english",
        raw_payload_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synchronizes Storefront details, pricing, genres, and developers for a game.
        Gracefully handles success=false or missing data without fabricating zero values.
        """
        source = self._ensure_steam_source()
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise ValueError(f"Game with id {game_id} not found")

        # Find Steam platform link
        game_platform = (
            self.db.query(GamePlatform)
            .filter(
                GamePlatform.game_id == game.id,
                GamePlatform.is_primary == True
            )
            .first()
        )
        if not game_platform:
            game_platform = self.db.query(GamePlatform).filter(GamePlatform.game_id == game.id).first()

        if not game_platform:
            raise ValueError(f"No platform link found for game {game.id}")

        appid = int(game_platform.external_id)

        # Fetch payload
        if raw_payload_override is not None:
            payload = raw_payload_override
        else:
            payload = await self.connector.get_app_details(
                appid=appid,
                country_code=country_code,
                language=language
            )

        # Save Raw Payload for auditability & provenance
        payload_str = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        raw_payload = RawPayload(
            id=uuid.uuid4(),
            source_id=source.id,
            request_fingerprint=f"appdetails:appid={appid}:cc={country_code}:l={language}",
            http_status=200,
            content_type="application/json",
            payload=payload,
            payload_hash=payload_hash,
            fetched_at=now_utc(),
            parser_version="storefront-v1"
        )
        self.db.add(raw_payload)

        appid_str = str(appid)
        app_entry = payload.get(appid_str, {})
        is_success = app_entry.get("success", False)

        if not is_success:
            # Record unavailable snapshot, do NOT invent zeroes
            price_snap = PriceSnapshot(
                observed_at=now_utc(),
                game_platform_id=game_platform.id,
                country_code=country_code.upper()[:2],
                currency="USD",
                regular_price_minor=None,
                final_price_minor=None,
                discount_percent=None,
                is_free=False,
                source_id=source.id,
                availability_status="unavailable",
                raw_payload_id=raw_payload.id
            )
            self.db.add(price_snap)
            self.db.commit()

            logger.warn("storefront_appdetails_unavailable", appid=appid)
            return {
                "success": False,
                "availability_status": "unavailable",
                "message": "Steam Storefront returned success=false for this application"
            }

        data = app_entry.get("data", {})

        # 1. Update Game attributes
        game.canonical_name = data.get("name", game.canonical_name)
        game.short_description = data.get("short_description")
        game.description = data.get("detailed_description")
        game.cover_image_url = data.get("header_image")
        game.website_url = data.get("website")

        # Type (game, dlc, demo, etc.)
        item_type = data.get("type", "game")
        game.game_type = item_type

        # Release date
        rel_info = data.get("release_date", {})
        coming_soon = rel_info.get("coming_soon", False)
        date_str = rel_info.get("date")
        parsed_d = parse_steam_date(date_str)
        if parsed_d:
            game.release_date = parsed_d
            game.release_date_precision = "day" if len(date_str.split(",")) > 1 else "year"
        game.release_status = "coming_soon" if coming_soon else "released"

        # Early Access category check (category id 26 is Early Access on Steam)
        categories = data.get("categories", [])
        is_ea = any(c.get("id") == 26 or "early access" in c.get("description", "").lower() for c in categories)
        game.is_early_access = is_ea
        game.updated_at = now_utc()

        # 2. Price snapshot
        is_free = data.get("is_free", False)
        price_overview = data.get("price_overview")
        currency = country_code.upper()

        if is_free:
            price_snap = PriceSnapshot(
                observed_at=now_utc(),
                game_platform_id=game_platform.id,
                country_code=country_code.upper()[:2],
                currency=price_overview.get("currency", "USD") if price_overview else "USD",
                regular_price_minor=0,
                final_price_minor=0,
                discount_percent=0,
                is_free=True,
                source_id=source.id,
                availability_status="available",
                raw_payload_id=raw_payload.id
            )
            self.db.add(price_snap)
        elif price_overview:
            # Currency in minor units (cents)
            regular_cents = price_overview.get("initial")
            final_cents = price_overview.get("final")
            discount_pct = price_overview.get("discount_percent")
            curr = price_overview.get("currency", "USD")

            price_snap = PriceSnapshot(
                observed_at=now_utc(),
                game_platform_id=game_platform.id,
                country_code=country_code.upper()[:2],
                currency=curr,
                regular_price_minor=regular_cents,
                final_price_minor=final_cents,
                discount_percent=discount_pct,
                is_free=False,
                source_id=source.id,
                availability_status="available",
                raw_payload_id=raw_payload.id
            )
            self.db.add(price_snap)
        else:
            # Unpriced / unavailable price
            price_snap = PriceSnapshot(
                observed_at=now_utc(),
                game_platform_id=game_platform.id,
                country_code=country_code.upper()[:2],
                currency="USD",
                regular_price_minor=None,
                final_price_minor=None,
                discount_percent=None,
                is_free=False,
                source_id=source.id,
                availability_status="unavailable",
                raw_payload_id=raw_payload.id
            )
            self.db.add(price_snap)

        # 3. Developers and Publishers
        for dev_name in data.get("developers", []):
            dev_name = dev_name.strip()
            if not dev_name:
                continue
            org = self.db.query(Organization).filter(Organization.canonical_name == dev_name).first()
            if not org:
                org = Organization(id=uuid.uuid4(), canonical_name=dev_name, created_at=now_utc())
                self.db.add(org)
                self.db.flush()
            # Link in game_developers
            link = self.db.query(GameDeveloper).filter(
                GameDeveloper.game_id == game.id,
                GameDeveloper.organization_id == org.id
            ).first()
            if not link:
                link = GameDeveloper(game_id=game.id, organization_id=org.id, source_id=source.id, observed_at=now_utc())
                self.db.add(link)

        for pub_name in data.get("publishers", []):
            pub_name = pub_name.strip()
            if not pub_name:
                continue
            org = self.db.query(Organization).filter(Organization.canonical_name == pub_name).first()
            if not org:
                org = Organization(id=uuid.uuid4(), canonical_name=pub_name, created_at=now_utc())
                self.db.add(org)
                self.db.flush()
            # Link in game_publishers
            link = self.db.query(GamePublisher).filter(
                GamePublisher.game_id == game.id,
                GamePublisher.organization_id == org.id
            ).first()
            if not link:
                link = GamePublisher(game_id=game.id, organization_id=org.id, source_id=source.id, observed_at=now_utc())
                self.db.add(link)

        # 4. Genres and Categories (Taxonomies)
        for g_item in data.get("genres", []):
            g_id = str(g_item.get("id"))
            g_name = g_item.get("description", "").strip()
            if not g_name:
                continue
            tax = self.db.query(TaxonomyItem).filter(
                TaxonomyItem.taxonomy_source == "steam_genre",
                TaxonomyItem.external_id == g_id
            ).first()
            if not tax:
                tax = TaxonomyItem(
                    id=uuid.uuid4(),
                    canonical_name=g_name,
                    taxonomy_source="steam_genre",
                    external_id=g_id,
                    language_code="en"
                )
                self.db.add(tax)
                self.db.flush()

            gt_link = self.db.query(GameTaxonomy).filter(
                GameTaxonomy.game_id == game.id,
                GameTaxonomy.taxonomy_id == tax.id
            ).first()
            if not gt_link:
                gt_link = GameTaxonomy(game_id=game.id, taxonomy_id=tax.id, source_id=source.id, observed_at=now_utc())
                self.db.add(gt_link)

        self.db.commit()

        logger.info("storefront_metadata_synced", game_id=str(game.id), appid=appid, name=game.canonical_name)

        return {
            "success": True,
            "game_id": str(game.id),
            "appid": appid,
            "name": game.canonical_name,
            "is_free": is_free,
            "has_price": bool(price_overview),
            "developers_count": len(data.get("developers", [])),
            "genres_count": len(data.get("genres", []))
        }
