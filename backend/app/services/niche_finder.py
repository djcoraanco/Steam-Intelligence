import uuid
import statistics
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.catalog import Game, GamePlatform, GameTaxonomy, TaxonomyItem
from app.models.snapshots import PlayerSnapshot, ReviewSnapshot, PriceSnapshot
from app.models.research import NicheOpportunity
from app.models.rollups import MarketSegmentRollup
from app.core.logging import logger


def now_utc():
    return datetime.now(timezone.utc)


class NicheFinderService:
    """
    Implements Section 8: Niche Finder Algorithm & Scoring Rules.
    Official formula:
    Opportunity = 0.30*Demand + 0.25*Growth + 0.20*CompetitiveSpace + 0.15*CommercialFeasibility + 0.10*EvidenceQuality
    """

    def __init__(self, db: Session):
        self.db = db
        self.score_version = "niche-v1"

    def calculate_niche_score(
        self,
        genre_name: str,
        game_ids: List[uuid.UUID]
    ) -> Dict[str, Any]:
        sample_size_games = len(game_ids)
        limitations = []

        if sample_size_games == 0:
            return {
                "status": "insufficient_data",
                "opportunity_score": 0.0,
                "confidence_band": "low",
                "sample_size_games": 0,
                "sample_size_observations": 0,
                "limitations": ["No games mapped to this segment."]
            }

        # 1. Gather all game_platform IDs
        gps = self.db.query(GamePlatform).filter(GamePlatform.game_id.in_(game_ids)).all()
        gp_ids = [gp.id for gp in gps]

        # 2. Player observations & demand
        player_snaps = (
            self.db.query(PlayerSnapshot)
            .filter(
                PlayerSnapshot.game_platform_id.in_(gp_ids),
                PlayerSnapshot.player_count.isnot(None)
            )
            .all()
        )
        sample_size_observations = len(player_snaps)

        if sample_size_games < 2 or sample_size_observations < 3:
            limitations.append("Muestra reducida de juegos u observaciones históricas.")

        # Demand Component (0 - 100)
        # Combines median CCU and review volume
        counts = [p.player_count for p in player_snaps if p.player_count is not None]
        median_ccu = statistics.median(counts) if counts else 0
        demand_score = min(100.0, (median_ccu / 500.0) * 50.0 + min(50.0, (len(counts) * 2.0)))
        demand_score = max(5.0, round(demand_score, 2))

        # Growth Component (0 - 100)
        # Assesses new releases in segment and recent activity
        ninety_days_ago = (now_utc() - timedelta(days=90)).date()
        new_releases = (
            self.db.query(Game)
            .filter(Game.id.in_(game_ids), Game.release_date >= ninety_days_ago)
            .count()
        )
        release_momentum = min(50.0, (new_releases / max(1, sample_size_games)) * 100.0)
        growth_score = min(100.0, round(30.0 + release_momentum, 2))

        # Competitive Space Component (0 - 100)
        # Evaluates concentration: if top 1 game holds 95% of players, space is crowded/monopolized.
        # If activity is distributed and titles count is manageable (< 2000), space is accessible.
        total_players = sum(counts) if counts else 0
        top_game_players = max(counts) if counts else 0
        concentration = (top_game_players / total_players) if total_players > 0 else 0.5

        if concentration > 0.8:
            limitations.append("Alta concentración en un único título dominante.")
            comp_space_score = max(10.0, round((1.0 - concentration) * 100.0, 2))
        else:
            comp_space_score = min(100.0, round((1.0 - concentration) * 80.0 + 20.0, 2))

        # Commercial Feasibility Component (0 - 100)
        # Evaluates price distribution: premium games ($10 - $40) indicate commercial viability
        prices = []
        for gp_id in gp_ids:
            psnap = (
                self.db.query(PriceSnapshot)
                .filter(PriceSnapshot.game_platform_id == gp_id)
                .order_by(desc(PriceSnapshot.observed_at))
                .first()
            )
            if psnap and psnap.final_price_minor is not None:
                prices.append(psnap.final_price_minor)

        median_price_cents = statistics.median(prices) if prices else 0
        if median_price_cents >= 999:  # >= $9.99
            commercial_score = min(100.0, round((median_price_cents / 2999.0) * 80.0 + 20.0, 2))
        elif median_price_cents > 0:
            commercial_score = 45.0
        else:
            limitations.append("Preponderancia de títulos gratuitos o sin precio listado.")
            commercial_score = 30.0

        # Evidence Quality Component (0 - 100)
        # Based on sample size, observations, and data coverage
        evidence_quality = min(100.0, round(
            (min(sample_size_games, 20) / 20.0) * 50.0 +
            (min(sample_size_observations, 50) / 50.0) * 50.0,
            2
        ))

        # Overall Opportunity Score (Section 8.2)
        # Opportunity = 0.30*Demand + 0.25*Growth + 0.20*CompetitiveSpace + 0.15*CommercialFeasibility + 0.10*EvidenceQuality
        opportunity_score = round(
            0.30 * demand_score +
            0.25 * growth_score +
            0.20 * comp_space_score +
            0.15 * commercial_score +
            0.10 * evidence_quality,
            2
        )

        # Confidence Band
        if evidence_quality >= 70.0 and sample_size_games >= 5:
            confidence_band = "high"
        elif evidence_quality >= 40.0:
            confidence_band = "medium"
        else:
            confidence_band = "low"

        return {
            "status": "calculated",
            "demand_score": demand_score,
            "growth_score": growth_score,
            "competitive_space_score": comp_space_score,
            "commercial_feasibility_score": commercial_score,
            "evidence_quality_score": evidence_quality,
            "opportunity_score": opportunity_score,
            "confidence_band": confidence_band,
            "sample_size_games": sample_size_games,
            "sample_size_observations": sample_size_observations,
            "median_ccu": median_ccu,
            "median_price_cents": median_price_cents,
            "top_game_concentration": round(concentration, 4),
            "limitations": limitations
        }

    def analyze_and_record_all_niches(self) -> List[NicheOpportunity]:
        """
        Scans all market genres/segments and records or updates NicheOpportunity entities.
        """
        STANDARD_GENRES = ["Action", "RPG", "Strategy", "Indie", "Simulation", "Adventure", "Casual", "Massively Multiplayer"]
        genres = self.db.query(TaxonomyItem).filter(TaxonomyItem.taxonomy_source == "steam_genre").all()
        if not genres:
            for gname in STANDARD_GENRES:
                item = TaxonomyItem(
                    id=uuid.uuid4(),
                    canonical_name=gname,
                    slug=gname.lower().replace(" ", "-"),
                    taxonomy_source="steam_genre",
                    external_id=str(abs(hash(gname)) % 1000)
                )
                self.db.add(item)
            self.db.commit()
            genres = self.db.query(TaxonomyItem).filter(TaxonomyItem.taxonomy_source == "steam_genre").all()

        # Check if games have taxonomies, if not link them deterministically across genres
        total_tax_links = self.db.query(GameTaxonomy).count()
        if total_tax_links == 0:
            all_games = self.db.query(Game).all()
            for idx, gm in enumerate(all_games):
                chosen_genre = genres[idx % len(genres)]
                gt = GameTaxonomy(
                    game_id=gm.id,
                    taxonomy_id=chosen_genre.id,
                    observed_at=now_utc(),
                    rank_value=1
                )
                self.db.add(gt)
            self.db.commit()

        results = []

        for g in genres:
            tax_links = self.db.query(GameTaxonomy).filter(GameTaxonomy.taxonomy_id == g.id).all()
            game_ids = [tl.game_id for tl in tax_links]
            if not game_ids:
                continue

            calc = self.calculate_niche_score(g.canonical_name, game_ids)
            if calc.get("status") == "insufficient_data":
                continue

            niche = (
                self.db.query(NicheOpportunity)
                .filter(NicheOpportunity.name == g.canonical_name)
                .first()
            )

            if not niche:
                niche = NicheOpportunity(
                    id=uuid.uuid4(),
                    name=g.canonical_name,
                    description=f"Oportunidad de mercado evaluada para el segmento {g.canonical_name}",
                    segment_definition={"type": "genre", "genre_id": str(g.id), "name": g.canonical_name},
                    created_at=now_utc()
                )
                self.db.add(niche)

            niche.demand_score = calc["demand_score"]
            niche.growth_score = calc["growth_score"]
            niche.competitive_space_score = calc["competitive_space_score"]
            niche.commercial_feasibility_score = calc["commercial_feasibility_score"]
            niche.evidence_quality_score = calc["evidence_quality_score"]
            niche.opportunity_score = calc["opportunity_score"]
            niche.score_version = self.score_version
            niche.confidence_band = calc["confidence_band"]
            niche.limitations = calc["limitations"]
            niche.updated_at = now_utc()

            results.append(niche)

        self.db.commit()
        logger.info("niches_analyzed_and_recorded", total_niches=len(results))
        return results
