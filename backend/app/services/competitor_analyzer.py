import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from app.models.catalog import Game, GamePlatform, GameTaxonomy, TaxonomyItem, Organization, GameDeveloper
from app.models.snapshots import PlayerSnapshot, PriceSnapshot, ReviewSnapshot
from app.models.competitors import GameCompetitor

logger = logging.getLogger(__name__)


class CompetitorAnalyzerService:
    def __init__(self, db: Session):
        self.db = db

    def suggest_competitors(self, target_game_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Calculates competitor suggestions using Jaccard similarity across taxonomy items (tags/genres)
        and proximity of release date/price.
        """
        target_game = self.db.query(Game).filter(Game.id == target_game_id).first()
        if not target_game:
            return []

        # Get target game taxonomy IDs
        target_tax_rows = self.db.query(GameTaxonomy.taxonomy_id).filter(
            GameTaxonomy.game_id == target_game.id
        ).all()
        target_tax_ids = set([t[0] for t in target_tax_rows])

        # Get all other games with taxonomy items
        other_games = self.db.query(Game).filter(Game.id != target_game.id).limit(100).all()
        candidates = []

        for candidate in other_games:
            cand_tax_rows = self.db.query(GameTaxonomy.taxonomy_id).filter(
                GameTaxonomy.game_id == candidate.id
            ).all()
            cand_tax_ids = set([t[0] for t in cand_tax_rows])

            intersection = target_tax_ids.intersection(cand_tax_ids)
            union = target_tax_ids.union(cand_tax_ids)

            jaccard = (len(intersection) / len(union)) if union else 0.0

            # Determine dominant reason
            reasons = []
            if jaccard > 0.4:
                reasons.append("tag_overlap")
            if target_game.is_early_access == candidate.is_early_access and candidate.is_early_access:
                reasons.append("early_access_cohort")
            if not reasons:
                reasons.append("genre_overlap" if jaccard > 0.1 else "audience_overlap")

            # Check matching taxonomy names
            matching_names = []
            if intersection:
                items = self.db.query(TaxonomyItem.canonical_name).filter(
                    TaxonomyItem.id.in_(list(intersection))
                ).all()
                matching_names = [i[0] for i in items]

            candidates.append({
                "game_id": str(candidate.id),
                "name": candidate.canonical_name,
                "similarity_score": round(jaccard, 4),
                "primary_reason": reasons[0],
                "all_reasons": reasons,
                "shared_tags_count": len(intersection),
                "shared_taxonomy": matching_names[:5],
                "release_date": candidate.release_date.isoformat() if candidate.release_date else None,
                "is_early_access": candidate.is_early_access
            })

        # Sort descending by similarity
        candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
        return candidates[:limit]

    def link_competitor(
        self,
        game_id: str,
        competitor_game_id: str,
        reason_type: str = "tag_overlap",
        similarity_score: Optional[float] = None,
        notes: Optional[Dict[str, Any]] = None
    ) -> GameCompetitor:
        """Manually or algorithmically records a competitor relationship."""
        existing = self.db.query(GameCompetitor).filter(
            GameCompetitor.game_id == game_id,
            GameCompetitor.competitor_game_id == competitor_game_id,
            GameCompetitor.reason_type == reason_type
        ).first()

        if existing:
            if similarity_score is not None:
                existing.similarity_score = similarity_score
            if notes is not None:
                existing.notes = notes
            self.db.commit()
            self.db.refresh(existing)
            return existing

        competitor_rel = GameCompetitor(
            id=uuid.uuid4(),
            game_id=game_id,
            competitor_game_id=competitor_game_id,
            reason_type=reason_type,
            similarity_score=similarity_score,
            notes=notes or {}
        )
        self.db.add(competitor_rel)
        self.db.commit()
        self.db.refresh(competitor_rel)
        return competitor_rel

    def list_linked_competitors(self, game_id: str) -> List[Dict[str, Any]]:
        """Returns all registered competitors for a game."""
        links = self.db.query(GameCompetitor).filter(GameCompetitor.game_id == game_id).all()
        results = []
        for l in links:
            comp_game = self.db.query(Game).filter(Game.id == l.competitor_game_id).first()
            if comp_game:
                results.append({
                    "id": str(l.id),
                    "competitor_game_id": str(comp_game.id),
                    "name": comp_game.canonical_name,
                    "reason_type": l.reason_type,
                    "similarity_score": float(l.similarity_score) if l.similarity_score else 0.0,
                    "notes": l.notes,
                    "created_at": l.created_at.isoformat() if l.created_at else None
                })
        return results

    def compare_head_to_head(self, game_id_a: str, game_id_b: str) -> Dict[str, Any]:
        """
        Direct side-by-side comparison matrix for two games.
        Includes pricing, CCU peaks, review stats, tags overlap, and metadata.
        """
        game_a = self.db.query(Game).filter(Game.id == game_id_a).first()
        game_b = self.db.query(Game).filter(Game.id == game_id_b).first()

        if not game_a or not game_b:
            raise ValueError("One or both game IDs not found")

        def get_game_metrics(game: Game):
            gp = self.db.query(GamePlatform).filter(GamePlatform.game_id == game.id).first()
            price_cents = None
            is_free = False
            latest_ccu = None
            peak_ccu = None
            total_reviews = None
            positive_ratio = None

            if gp:
                price = self.db.query(PriceSnapshot).filter(
                    PriceSnapshot.game_platform_id == gp.id
                ).order_by(PriceSnapshot.observed_at.desc()).first()
                if price:
                    price_cents = price.final_price_minor
                    is_free = price.is_free

                players_q = self.db.query(PlayerSnapshot.player_count).filter(
                    PlayerSnapshot.game_platform_id == gp.id,
                    PlayerSnapshot.availability_status == "available"
                )
                peak_ccu_val = players_q.order_by(PlayerSnapshot.player_count.desc()).first()
                if peak_ccu_val:
                    peak_ccu = peak_ccu_val[0]

                latest_player = self.db.query(PlayerSnapshot).filter(
                    PlayerSnapshot.game_platform_id == gp.id,
                    PlayerSnapshot.availability_status == "available"
                ).order_by(PlayerSnapshot.observed_at.desc()).first()
                if latest_player:
                    latest_ccu = latest_player.player_count

                reviews = self.db.query(ReviewSnapshot).filter(
                    ReviewSnapshot.game_platform_id == gp.id
                ).order_by(ReviewSnapshot.observed_at.desc()).first()
                if reviews:
                    total_reviews = reviews.total_reviews
                    positive_ratio = float(reviews.positive_ratio) if reviews.positive_ratio is not None else None

            # Taxonomies
            tax_items = self.db.query(TaxonomyItem.canonical_name).join(
                GameTaxonomy, GameTaxonomy.taxonomy_id == TaxonomyItem.id
            ).filter(GameTaxonomy.game_id == game.id).all()
            tags = [t[0] for t in tax_items]

            return {
                "id": str(game.id),
                "name": game.canonical_name,
                "release_date": game.release_date.isoformat() if game.release_date else None,
                "is_early_access": bool(game.is_early_access),
                "price_usd": round(price_cents / 100.0, 2) if price_cents is not None else None,
                "is_free": is_free,
                "latest_ccu": latest_ccu,
                "peak_ccu": peak_ccu,
                "total_reviews": total_reviews,
                "positive_ratio": round(positive_ratio * 100, 1) if positive_ratio is not None else None,
                "tags": tags
            }

        metrics_a = get_game_metrics(game_a)
        metrics_b = get_game_metrics(game_b)

        # Overlap analysis
        tags_a = set(metrics_a["tags"])
        tags_b = set(metrics_b["tags"])
        shared_tags = list(tags_a.intersection(tags_b))
        unique_a = list(tags_a.difference(tags_b))
        unique_b = list(tags_b.difference(tags_a))
        jaccard = len(shared_tags) / len(tags_a.union(tags_b)) if (tags_a or tags_b) else 0.0

        return {
            "game_a": metrics_a,
            "game_b": metrics_b,
            "comparison": {
                "shared_tags": shared_tags,
                "unique_to_a": unique_a,
                "unique_to_b": unique_b,
                "tag_similarity_index": round(jaccard, 4),
                "price_difference_usd": round((metrics_a["price_usd"] or 0) - (metrics_b["price_usd"] or 0), 2),
                "ccu_ratio": round(metrics_a["latest_ccu"] / metrics_b["latest_ccu"], 2) if (metrics_a["latest_ccu"] and metrics_b["latest_ccu"]) else None,
                "positive_ratio_diff": round((metrics_a["positive_ratio"] or 0) - (metrics_b["positive_ratio"] or 0), 1)
            }
        }
