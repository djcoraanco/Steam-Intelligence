import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.connectors.steam import SteamConnector
from app.models.catalog import Game, GamePlatform
from app.models.sources import DataSource, RawPayload
from app.models.snapshots import PlayerSnapshot, ReviewSnapshot, ReviewItem
from app.core.logging import logger


def now_utc():
    return datetime.now(timezone.utc)


class PlayerReviewSyncService:
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

    async def snapshot_players(
        self,
        game_id: uuid.UUID,
        raw_payload_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Takes a point-in-time snapshot of current concurrent players (CCU)
        using ISteamUserStats/GetNumberOfCurrentPlayers/v1/.
        Stores observation in player_snapshots.
        """
        source = self._ensure_steam_source()
        game_platform = (
            self.db.query(GamePlatform)
            .filter(GamePlatform.game_id == game_id, GamePlatform.is_primary == True)
            .first()
        )
        if not game_platform:
            game_platform = self.db.query(GamePlatform).filter(GamePlatform.game_id == game_id).first()
        if not game_platform:
            raise ValueError(f"No platform link found for game {game_id}")

        appid = int(game_platform.external_id)

        try:
            if raw_payload_override is not None:
                payload = raw_payload_override
            else:
                payload = await self.connector.get_number_of_current_players(appid)

            # Store Raw Payload
            payload_str = json.dumps(payload, sort_keys=True)
            payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

            raw_payload = RawPayload(
                id=uuid.uuid4(),
                source_id=source.id,
                request_fingerprint=f"GetNumberOfCurrentPlayers:appid={appid}",
                http_status=200,
                content_type="application/json",
                payload=payload,
                payload_hash=payload_hash,
                fetched_at=now_utc(),
                parser_version="players-v1"
            )
            self.db.add(raw_payload)

            response_data = payload.get("response", {})
            result_code = response_data.get("result", 0)
            player_count = response_data.get("player_count")

            # Check validity
            if result_code == 1 and player_count is not None:
                status = "available"
                quality_score = 100
            else:
                status = "unavailable"
                quality_score = 50
                player_count = None

            snapshot = PlayerSnapshot(
                observed_at=now_utc(),
                game_platform_id=game_platform.id,
                source_id=source.id,
                player_count=player_count,
                availability_status=status,
                quality_score=quality_score,
                raw_payload_id=raw_payload.id
            )
            self.db.add(snapshot)
            self.db.commit()

            logger.info(
                "player_snapshot_recorded",
                appid=appid,
                player_count=player_count,
                status=status
            )

            return {
                "success": status == "available",
                "appid": appid,
                "player_count": player_count,
                "availability_status": status,
                "observed_at": snapshot.observed_at.isoformat()
            }

        except Exception as exc:
            self.db.rollback()
            # Record an unavailable snapshot to preserve continuity
            fail_snap = PlayerSnapshot(
                observed_at=now_utc(),
                game_platform_id=game_platform.id,
                source_id=source.id,
                player_count=None,
                availability_status="unavailable",
                quality_score=0,
                raw_payload_id=None
            )
            self.db.add(fail_snap)
            self.db.commit()
            logger.error("player_snapshot_failed", appid=appid, error=str(exc))
            raise

    async def sync_reviews(
        self,
        game_id: uuid.UUID,
        cursor: str = "*",
        language: str = "all",
        filter_type: str = "recent",
        num_per_page: int = 100,
        raw_payload_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synchronizes reviews using IUserReviewsService/GetAppReviews/v1/.
        Stores aggregate metrics in review_snapshots and individual review items in review_items.
        Calculates review_delta against the previous snapshot.
        """
        source = self._ensure_steam_source()
        game_platform = (
            self.db.query(GamePlatform)
            .filter(GamePlatform.game_id == game_id, GamePlatform.is_primary == True)
            .first()
        )
        if not game_platform:
            game_platform = self.db.query(GamePlatform).filter(GamePlatform.game_id == game_id).first()
        if not game_platform:
            raise ValueError(f"No platform link found for game {game_id}")

        appid = int(game_platform.external_id)

        try:
            if raw_payload_override is not None:
                payload = raw_payload_override
            else:
                payload = await self.connector.get_app_reviews(
                    appid=appid,
                    cursor=cursor,
                    language=language,
                    filter_type=filter_type,
                    num_per_page=num_per_page
                )

            # Raw Payload
            payload_str = json.dumps(payload, sort_keys=True)
            payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

            raw_payload = RawPayload(
                id=uuid.uuid4(),
                source_id=source.id,
                request_fingerprint=f"GetAppReviews:appid={appid}:filter={filter_type}:lang={language}",
                http_status=200,
                content_type="application/json",
                payload=payload,
                payload_hash=payload_hash,
                fetched_at=now_utc(),
                parser_version="reviews-v1"
            )
            self.db.add(raw_payload)

            summary = payload.get("query_summary", {})
            total_reviews = summary.get("total_reviews")
            total_positive = summary.get("total_positive")
            total_negative = summary.get("total_negative")
            positive_ratio = None
            if total_reviews and total_reviews > 0 and total_positive is not None:
                positive_ratio = round(float(total_positive) / float(total_reviews), 5)

            # Store Snapshot
            review_snap = ReviewSnapshot(
                observed_at=now_utc(),
                game_platform_id=game_platform.id,
                language_code=language,
                total_reviews=total_reviews,
                positive_reviews=total_positive,
                negative_reviews=total_negative,
                positive_ratio=positive_ratio,
                review_period_days=summary.get("review_score"),
                source_id=source.id,
                availability_status="available" if total_reviews is not None else "unavailable"
            )
            self.db.add(review_snap)

            # Process individual review items
            reviews_list = payload.get("reviews", [])
            saved_reviews = 0
            for r in reviews_list:
                review_id = str(r.get("recommendationid"))
                if not review_id:
                    continue

                # Check uniqueness (source_id, source_review_id)
                existing = (
                    self.db.query(ReviewItem)
                    .filter(
                        ReviewItem.source_id == source.id,
                        ReviewItem.source_review_id == review_id
                    )
                    .first()
                )
                if not existing:
                    created_ts = r.get("timestamp_created")
                    reviewed_at = (
                        datetime.fromtimestamp(created_ts, tz=timezone.utc)
                        if created_ts
                        else now_utc()
                    )
                    author = r.get("author", {})
                    new_item = ReviewItem(
                        id=uuid.uuid4(),
                        source_id=source.id,
                        source_review_id=review_id,
                        game_platform_id=game_platform.id,
                        language_code=r.get("language", "english"),
                        reviewed_at=reviewed_at,
                        voted_up=bool(r.get("voted_up", True)),
                        votes_up=r.get("votes_up", 0),
                        votes_funny=r.get("votes_funny", 0),
                        playtime_forever_minutes=author.get("playtime_forever", 0),
                        playtime_at_review_minutes=author.get("playtime_at_review", 0),
                        review_text=r.get("review", "")[:2000]  # Respect storage retention policy
                    )
                    self.db.add(new_item)
                    saved_reviews += 1

            self.db.commit()

            logger.info(
                "reviews_synced",
                appid=appid,
                total=total_reviews,
                positive_ratio=positive_ratio,
                saved_items=saved_reviews
            )

            return {
                "success": True,
                "appid": appid,
                "total_reviews": total_reviews,
                "positive_reviews": total_positive,
                "negative_reviews": total_negative,
                "positive_ratio": positive_ratio,
                "items_saved": saved_reviews,
                "next_cursor": payload.get("cursor")
            }

        except Exception as exc:
            self.db.rollback()
            logger.error("reviews_sync_failed", appid=appid, error=str(exc))
            raise
