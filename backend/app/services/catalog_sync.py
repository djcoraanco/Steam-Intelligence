import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.connectors.steam import SteamConnector
from app.models.catalog import Platform, Game, GamePlatform
from app.models.sources import DataSource, RawPayload
from app.models.checkpoints import IngestionCheckpoint
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

        try:
            if raw_payload_override is not None:
                payload = raw_payload_override
            else:
                payload = await self.connector.get_app_list(
                    last_appid=last_appid,
                    max_results=max_results,
                    if_modified_since=checkpoint.last_modified,
                    include_games=include_games,
                    include_dlc=include_dlc
                )

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

                if existing_gp:
                    existing_gp.last_seen_at = now_utc()
                    # Update canonical name if game already exists
                    if existing_gp.game:
                        existing_gp.game.canonical_name = name
                        existing_gp.game.updated_at = now_utc()
                    updated_count += 1
                else:
                    # Create new Game
                    new_game = Game(
                        id=uuid.uuid4(),
                        canonical_name=name,
                        game_type="dlc" if include_dlc and not include_games else "game",
                        release_status="released",
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
                    imported_count += 1

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
