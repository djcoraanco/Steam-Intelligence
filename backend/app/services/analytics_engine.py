import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import statistics
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.catalog import Game, GamePlatform, GameTaxonomy, TaxonomyItem
from app.models.snapshots import PlayerSnapshot, ReviewSnapshot, PriceSnapshot
from app.models.rollups import GameMetricRollup, MarketSegmentRollup
from app.core.logging import logger


def now_utc():
    return datetime.now(timezone.utc)


def calculate_growth_rate(current: Optional[float], baseline: Optional[float], min_sample: float = 1.0) -> Optional[float]:
    """
    Deterministic growth calculation complying with Section 7.4 of the Master Specification.
    - If baseline is None or 0: returns None (never Infinity or divide-by-zero).
    - If baseline is smaller than min_sample threshold: flagged or returns standard percentage.
    """
    if current is None or baseline is None:
        return None
    if baseline <= 0:
        return None
    return round(((current - baseline) / baseline) * 100.0, 2)


class AnalyticsEngine:
    def __init__(self, db: Session):
        self.db = db

    def compute_game_rollups(
        self,
        game_platform_id: uuid.UUID,
        period_type: str = "day",
        reference_time: Optional[datetime] = None
    ) -> GameMetricRollup:
        """
        Computes deterministic daily/weekly metrics for a game platform.
        Rolls up player snapshots, review deltas, and price observations.
        """
        ref_time = reference_time or now_utc()
        if period_type == "day":
            period_start = ref_time.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
            expected_observations = 96  # 15 min intervals
        elif period_type == "week":
            period_start = (ref_time - timedelta(days=ref_time.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=7)
            expected_observations = 96 * 7
        else:
            raise ValueError(f"Unsupported period_type: {period_type}")

        # 1. Player snapshots in window
        player_snaps = (
            self.db.query(PlayerSnapshot)
            .filter(
                PlayerSnapshot.game_platform_id == game_platform_id,
                PlayerSnapshot.observed_at >= period_start,
                PlayerSnapshot.observed_at < period_end,
                PlayerSnapshot.player_count.isnot(None)
            )
            .all()
        )

        counts = [p.player_count for p in player_snaps if p.player_count is not None]
        avg_players = round(statistics.mean(counts), 2) if counts else None
        max_players = max(counts) if counts else None
        min_players = min(counts) if counts else None
        obs_count = len(counts)

        data_coverage = min(100.0, round((obs_count / expected_observations) * 100.0, 2)) if obs_count > 0 else 0.0

        # 2. Review delta in window
        review_snaps = (
            self.db.query(ReviewSnapshot)
            .filter(
                ReviewSnapshot.game_platform_id == game_platform_id,
                ReviewSnapshot.observed_at >= period_start,
                ReviewSnapshot.observed_at < period_end
            )
            .order_by(ReviewSnapshot.observed_at.asc())
            .all()
        )

        review_delta = None
        if len(review_snaps) >= 2:
            first_count = review_snaps[0].total_reviews or 0
            last_count = review_snaps[-1].total_reviews or 0
            review_delta = max(0, last_count - first_count)
        elif len(review_snaps) == 1:
            # Check previous snapshot before period_start
            prev_snap = (
                self.db.query(ReviewSnapshot)
                .filter(
                    ReviewSnapshot.game_platform_id == game_platform_id,
                    ReviewSnapshot.observed_at < period_start
                )
                .order_by(ReviewSnapshot.observed_at.desc())
                .first()
            )
            if prev_snap and prev_snap.total_reviews is not None and review_snaps[0].total_reviews is not None:
                review_delta = max(0, review_snaps[0].total_reviews - prev_snap.total_reviews)

        # 3. Price snapshots in window
        price_snaps = (
            self.db.query(PriceSnapshot)
            .filter(
                PriceSnapshot.game_platform_id == game_platform_id,
                PriceSnapshot.observed_at >= period_start,
                PriceSnapshot.observed_at < period_end,
                PriceSnapshot.final_price_minor.isnot(None)
            )
            .all()
        )

        prices = [p.final_price_minor for p in price_snaps if p.final_price_minor is not None]
        price_min_minor = min(prices) if prices else None
        price_max_minor = max(prices) if prices else None
        discount_days = sum(1 for p in price_snaps if p.discount_percent and p.discount_percent > 0)

        # Upsert into game_metric_rollups
        calc_version = "analytics-v1"
        rollup = (
            self.db.query(GameMetricRollup)
            .filter(
                GameMetricRollup.game_platform_id == game_platform_id,
                GameMetricRollup.period_start == period_start,
                GameMetricRollup.period_type == period_type,
                GameMetricRollup.calculation_version == calc_version
            )
            .first()
        )

        if not rollup:
            rollup = GameMetricRollup(
                game_platform_id=game_platform_id,
                period_start=period_start,
                period_type=period_type,
                calculation_version=calc_version
            )
            self.db.add(rollup)

        rollup.avg_players = avg_players
        rollup.max_players = max_players
        rollup.min_players = min_players
        rollup.player_observation_count = obs_count
        rollup.review_delta = review_delta
        rollup.price_min_minor = price_min_minor
        rollup.price_max_minor = price_max_minor
        rollup.discount_days = discount_days
        rollup.data_coverage = data_coverage

        self.db.commit()
        return rollup

    def compute_all_market_segment_rollups(self, period_type: str = "day") -> List[MarketSegmentRollup]:
        """
        Computes aggregate metrics for genres and taxonomies.
        Avoids false sums, computes true medians and top-game concentration.
        """
        period_start = now_utc().replace(hour=0, minute=0, second=0, microsecond=0)
        calc_version = "analytics-v1"
        rollups = []

        genres = self.db.query(TaxonomyItem).filter(TaxonomyItem.taxonomy_source == "steam_genre").all()

        for genre in genres:
            # Find all games linked to this genre
            tax_links = self.db.query(GameTaxonomy).filter(GameTaxonomy.taxonomy_id == genre.id).all()
            game_ids = [tl.game_id for tl in tax_links]
            game_count = len(game_ids)
            if game_count == 0:
                continue

            # Find game_platforms
            gps = self.db.query(GamePlatform).filter(GamePlatform.game_id.in_(game_ids)).all()
            gp_ids = [gp.id for gp in gps]

            # Get latest players per game
            latest_players_by_gp = {}
            for gp_id in gp_ids:
                snap = (
                    self.db.query(PlayerSnapshot)
                    .filter(PlayerSnapshot.game_platform_id == gp_id)
                    .order_by(desc(PlayerSnapshot.observed_at))
                    .first()
                )
                if snap and snap.player_count is not None:
                    latest_players_by_gp[gp_id] = snap.player_count

            player_counts = list(latest_players_by_gp.values())
            active_game_count = sum(1 for c in player_counts if c > 0)
            player_sum = sum(player_counts) if player_counts else 0

            # Top game concentration (Top 1 game player share)
            top_concentration = None
            if player_sum > 0 and player_counts:
                top_player = max(player_counts)
                top_concentration = round(float(top_player) / float(player_sum), 4)

            # Prices in segment
            prices_in_segment = []
            for gp_id in gp_ids:
                psnap = (
                    self.db.query(PriceSnapshot)
                    .filter(PriceSnapshot.game_platform_id == gp_id)
                    .order_by(desc(PriceSnapshot.observed_at))
                    .first()
                )
                if psnap and psnap.final_price_minor is not None:
                    prices_in_segment.append(psnap.final_price_minor)

            median_price = int(statistics.median(prices_in_segment)) if prices_in_segment else None

            # New releases count (last 60 days)
            sixty_days_ago = (now_utc() - timedelta(days=60)).date()
            new_releases = (
                self.db.query(Game)
                .filter(Game.id.in_(game_ids), Game.release_date >= sixty_days_ago)
                .count()
            )

            # Upsert into market_segment_rollups
            rollup = (
                self.db.query(MarketSegmentRollup)
                .filter(
                    MarketSegmentRollup.segment_type == "genre",
                    MarketSegmentRollup.period_start == period_start,
                    MarketSegmentRollup.period_type == period_type,
                    MarketSegmentRollup.calculation_version == calc_version
                )
                .first()
            )

            seg_key = {"genre_id": str(genre.id), "canonical_name": genre.canonical_name}

            # Check if this exact segment key exists
            existing_rollup = None
            all_rollups = self.db.query(MarketSegmentRollup).filter(
                MarketSegmentRollup.segment_type == "genre",
                MarketSegmentRollup.period_start == period_start,
                MarketSegmentRollup.period_type == period_type
            ).all()
            for r in all_rollups:
                if r.segment_key.get("genre_id") == str(genre.id):
                    existing_rollup = r
                    break

            if not existing_rollup:
                existing_rollup = MarketSegmentRollup(
                    segment_type="genre",
                    segment_key=seg_key,
                    period_start=period_start,
                    period_type=period_type,
                    calculation_version=calc_version
                )
                self.db.add(existing_rollup)

            existing_rollup.game_count = game_count
            existing_rollup.active_game_count = active_game_count
            existing_rollup.player_sum = player_sum
            existing_rollup.median_price_minor = median_price
            existing_rollup.new_release_count = new_releases
            existing_rollup.top_game_concentration = top_concentration
            existing_rollup.data_coverage = 100.0

            rollups.append(existing_rollup)

        self.db.commit()
        return rollups
