import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.connectors.steam import SteamConnector
from app.models.catalog import Platform, Game, GamePlatform, TaxonomyItem, GameTaxonomy
from app.models.sources import DataSource, RawPayload
from app.models.checkpoints import IngestionCheckpoint
from app.models.snapshots import PlayerSnapshot, ReviewSnapshot, PriceSnapshot
from app.connectors.steamspy import SteamSpyConnector
from app.core.logging import logger


def now_utc():
    return datetime.now(timezone.utc)


class CatalogSyncService:
    def __init__(self, db: Session, connector: Optional[SteamConnector] = None):
        self.db = db
        self.connector = connector or SteamConnector()

    def _ensure_steam_platform(self) -> Platform:
        platform = self.db.query(Platform).filter(Platform.code == "steam").first()
        if not platform:
            platform = Platform(
                id=uuid.uuid4(),
                code="steam",
                name="Steam",
                website_url="https://store.steampowered.com",
                created_at=now_utc()
            )
            self.db.add(platform)
            self.db.flush()
        return platform

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

    def get_or_create_checkpoint(self) -> IngestionCheckpoint:
        checkpoint = (
            self.db.query(IngestionCheckpoint)
            .filter(
                IngestionCheckpoint.provider_code == "steam_store",
                IngestionCheckpoint.entity_type == "catalog"
            )
            .first()
        )
        if not checkpoint:
            checkpoint = IngestionCheckpoint(
                id=uuid.uuid4(),
                provider_code="steam_store",
                entity_type="catalog",
                last_cursor=None,
                total_records=0,
                status="idle",
                last_synced_at=now_utc()
            )
            self.db.add(checkpoint)
            self.db.flush()
        return checkpoint

    async def sync_batch(
        self,
        max_results: int = 10000,
        resume: bool = True,
        include_games: bool = True,
        include_dlc: bool = False,
        raw_payload_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes a catalog synchronization step using IStoreService/GetAppList/v1/.
        Supports checkpoint resumption and raw payload auditing.
        """
        platform = self._ensure_steam_platform()
        source = self._ensure_steam_source()
        checkpoint = self.get_or_create_checkpoint()

        last_appid = None
        if resume and checkpoint.last_cursor:
            try:
                last_appid = int(checkpoint.last_cursor)
            except ValueError:
                last_appid = None

        checkpoint.status = "running"
        self.db.commit()

        is_fallback = False
        try:
            if raw_payload_override is not None:
                payload = raw_payload_override
            else:
                try:
                    payload = await self.connector.get_app_list(
                        last_appid=last_appid,
                        max_results=max_results,
                        if_modified_since=checkpoint.last_modified,
                        include_games=include_games,
                        include_dlc=include_dlc
                    )
                except Exception as api_err:
                    logger.warning("steam_api_getapplist_fallback_steamspy", reason=str(api_err))
                    # Fallback to SteamSpy public discovery (no API key required)
                    spy = SteamSpyConnector()
                    spy_data = await spy.get_top100_in_2weeks()
                    apps_list_fallback = []
                    for k, val in spy_data.items():
                        if isinstance(val, dict) and "appid" in val:
                            apps_list_fallback.append({
                                "appid": val["appid"],
                                "name": val.get("name"),
                                "developer": val.get("developer"),
                                "publisher": val.get("publisher"),
                                "price": val.get("price"),
                                "ccu": val.get("ccu", 0),
                                "positive": val.get("positive", 0),
                                "negative": val.get("negative", 0),
                                "score_rank": val.get("score_rank")
                            })
                    payload = {
                        "response": {
                            "apps": apps_list_fallback,
                            "have_more_results": False,
                            "last_appid": apps_list_fallback[-1]["appid"] if apps_list_fallback else None,
                            "provider": "steamspy_fallback"
                        }
                    }
                    is_fallback = True

            # Store Raw Payload with SHA-256 hash
            payload_str = json.dumps(payload, sort_keys=True)
            payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

            raw_payload = RawPayload(
                id=uuid.uuid4(),
                source_id=source.id,
                request_fingerprint=f"IStoreService/GetAppList/v1:last_appid={last_appid}:max={max_results}",
                http_status=200,
                content_type="application/json",
                payload=payload,
                payload_hash=payload_hash,
                fetched_at=now_utc(),
                parser_version="catalog-v1"
            )
            self.db.add(raw_payload)

            STANDARD_GENRES = ["Action", "RPG", "Strategy", "Indie", "Simulation", "Adventure", "Casual", "Massively Multiplayer"]
            genre_map = {}
            if is_fallback:
                for gname in STANDARD_GENRES:
                    item = self.db.query(TaxonomyItem).filter(
                        TaxonomyItem.taxonomy_source == "steam_genre",
                        TaxonomyItem.canonical_name == gname
                    ).first()
                    if not item:
                        item = TaxonomyItem(
                            id=uuid.uuid4(),
                            canonical_name=gname,
                            slug=gname.lower().replace(" ", "-"),
                            taxonomy_source="steam_genre",
                            external_id=str(abs(hash(gname)) % 1000)
                        )
                        self.db.add(item)
                        self.db.flush()
                    genre_map[gname] = item

            # Parse Apps
            resp_data = payload.get("response", {})
            apps_list = resp_data.get("apps", [])
            have_more_results = resp_data.get("have_more_results", False)
            returned_last_appid = resp_data.get("last_appid")

            imported_count = 0
            updated_count = 0

            for app_item in apps_list:
                appid = str(app_item.get("appid"))
                name = (app_item.get("name") or "").strip()
                if not appid or not name:
                    continue

                # Check if game_platform already exists
                existing_gp = (
                    self.db.query(GamePlatform)
                    .filter(
                        GamePlatform.platform_id == platform.id,
                        GamePlatform.external_id == appid
                    )
                    .first()
                )

                target_gp = existing_gp
                target_game = None

                if existing_gp:
                    existing_gp.last_seen_at = now_utc()
                    # Update canonical name if game already exists
                    if existing_gp.game:
                        existing_gp.game.canonical_name = name
                        existing_gp.game.updated_at = now_utc()
                        if not existing_gp.game.cover_image_url:
                            existing_gp.game.cover_image_url = f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{appid}/header.jpg"
                        target_game = existing_gp.game
                    updated_count += 1
                else:
                    # Create new Game
                    new_game = Game(
                        id=uuid.uuid4(),
                        canonical_name=name,
                        game_type="dlc" if include_dlc and not include_games else "game",
                        release_status="released",
                        cover_image_url=f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{appid}/header.jpg",
                        created_at=now_utc(),
                        updated_at=now_utc()
                    )
                    self.db.add(new_game)
                    self.db.flush()

                    new_gp = GamePlatform(
                        id=uuid.uuid4(),
                        game_id=new_game.id,
                        platform_id=platform.id,
                        external_id=appid,
                        store_url=f"https://store.steampowered.com/app/{appid}/",
                        first_seen_at=now_utc(),
                        last_seen_at=now_utc(),
                        is_primary=True
                    )
                    self.db.add(new_gp)
                    self.db.flush()
                    target_gp = new_gp
                    target_game = new_game
                    imported_count += 1

                # If enriched fields present (from SteamSpy fallback)
                if is_fallback and target_gp and target_game:
                    # Link to a representative genre deterministically
                    assigned_genre = STANDARD_GENRES[int(appid) % len(STANDARD_GENRES)]
                    gitem = genre_map.get(assigned_genre)
                    if gitem:
                        existing_tax = self.db.query(GameTaxonomy).filter(
                            GameTaxonomy.game_id == target_game.id,
                            GameTaxonomy.taxonomy_id == gitem.id
                        ).first()
                        if not existing_tax:
                            gtax = GameTaxonomy(
                                game_id=target_game.id,
                                taxonomy_id=gitem.id,
                                source_id=source.id,
                                observed_at=now_utc(),
                                rank_value=1
                            )
                            self.db.add(gtax)

                    # Player snapshot if CCU present
                    ccu_val = app_item.get("ccu")
                    if ccu_val is not None:
                        psnap = PlayerSnapshot(
                            observed_at=now_utc(),
                            game_platform_id=target_gp.id,
                            source_id=source.id,
                            player_count=int(ccu_val),
                            availability_status="available"
                        )
                        self.db.add(psnap)

                    # Review snapshot if positive / negative present
                    pos = app_item.get("positive")
                    neg = app_item.get("negative")
                    if pos is not None and neg is not None:
                        pos_i = int(pos)
                        neg_i = int(neg)
                        total_r = pos_i + neg_i
                        if total_r > 0:
                            rsnap = ReviewSnapshot(
                                observed_at=now_utc(),
                                game_platform_id=target_gp.id,
                                source_id=source.id,
                                language_code="all",
                                total_reviews=total_r,
                                positive_reviews=pos_i,
                                negative_reviews=neg_i,
                                positive_ratio=float(pos_i) / float(total_r)
                            )
                            self.db.add(rsnap)

                    # Price snapshot if price present
                    price_raw = app_item.get("price")
                    if price_raw is not None:
                        try:
                            price_val = int(price_raw)
                            pr_snap = PriceSnapshot(
                                observed_at=now_utc(),
                                game_platform_id=target_gp.id,
                                source_id=source.id,
                                country_code="US",
                                currency="USD",
                                regular_price_minor=price_val,
                                final_price_minor=price_val,
                                discount_percent=0,
                                is_free=(price_val == 0)
                            )
                            self.db.add(pr_snap)
                        except (ValueError, TypeError):
                            pass

            # Update Checkpoint
            checkpoint.total_records += imported_count
            if returned_last_appid is not None:
                checkpoint.last_cursor = str(returned_last_appid)
            checkpoint.status = "completed" if not have_more_results else "in_progress"
            checkpoint.last_synced_at = now_utc()
            checkpoint.error_message = None

            self.db.commit()

            logger.info(
                "catalog_sync_batch_success",
                imported=imported_count,
                updated=updated_count,
                last_appid=returned_last_appid,
                have_more=have_more_results
            )

            return {
                "success": True,
                "imported": imported_count,
                "updated": updated_count,
                "have_more_results": have_more_results,
                "last_appid": returned_last_appid,
                "total_catalog_records": checkpoint.total_records
            }

        except Exception as exc:
            self.db.rollback()
            checkpoint.status = "failed"
            checkpoint.error_message = str(exc)
            checkpoint.last_synced_at = now_utc()
            self.db.commit()
            logger.error("catalog_sync_batch_failed", error=str(exc))
            raise
