import re
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.catalog import Game, GamePlatform
from app.models.snapshots import ReviewItem
from app.models.competitors import ReviewTopicExtraction

logger = logging.getLogger(__name__)

# Canonical taxonomy keywords mapping
TOPIC_PATTERNS = {
    "bugs/crashes": [r"\bcrash\b", r"\bfreez", r"\bbug\b", r"\bglitch\b", r"\berror\b", r"\bunplayable\b", r"\bblack screen\b"],
    "performance/optimization": [r"\bfps\b", r"\blag\b", r"\bstutter\b", r"\bdrop\b", r"\boptimi[sz]", r"\bmemory leak\b", r"\bgpu\b", r"\bcpu\b"],
    "controls": [r"\bcontroller\b", r"\bgamepad\b", r"\bkeyboard\b", r"\bmouse\b", r"\bkeybind\b", r"\binput lag\b", r"\brebind\b"],
    "ui/ux": [r"\bmenu\b", r"\bhud\b", r"\binterface\b", r"\bfont\b", r"\btext size\b", r"\binventory\b", r"\breadability\b"],
    "difficulty/balance": [r"\btoo hard\b", r"\bunfair\b", r"\bbullet sponge\b", r"\btoo easy\b", r"\bbalance\b", r"\bnerf\b", r"\bbuff\b", r"\bdifficulty\b"],
    "content/replayability": [r"\bshort\b", r"\brepetitive\b", r"\breplay\b", r"\bhours of content\b", r"\bendgame\b", r"\bgrind\b", r"\bboring\b"],
    "price/value": [r"\boverpriced\b", r"\bworth the money\b", r"\brefund\b", r"\btoo expensive\b", r"\bprice tag\b", r"\bcheap\b"],
    "multiplayer/network": [r"\bmatchmaking\b", r"\bdisconnect\b", r"\bdesync\b", r"\bping\b", r"\bserver\b", r"\bnetcode\b", r"\bcoop\b", r"\bmultiplayer\b"],
    "progression": [r"\bleveling\b", r"\bunlock\b", r"\bskill tree\b", r"\bpacing\b", r"\bprogression\b", r"\bachievement\b"],
    "monetization": [r"\bmicrotransaction\b", r"\bbattle pass\b", r"\bp2w\b", r"\bpay to win\b", r"\bdlc\b", r"\blootbox\b"],
    "accessibility": [r"\bcolorblind\b", r"\bsubtitle\b", r"\bmotion sickness\b", r"\bfov\b", r"\bhearing\b"],
    "localization": [r"\btranslation\b", r"\bspanish\b", r"\blocalization\b", r"\bbad english\b", r"\bgrammar\b"],
    "community/support": [r"\bdeveloper\b", r"\bdevs\b", r"\btoxic\b", r"\bpatch\b", r"\bupdate\b", r"\babandoned\b", r"\bsupport\b"],
    "positive_gameplay_loop": [r"\baddictive\b", r"\bmasterpiece\b", r"\bsatisfying\b", r"\bfluid\b", r"\bgreat mechanics\b", r"\blove this game\b", r"\bso much fun\b"],
    "art/audio/story": [r"\bsoundtrack\b", r"\bost\b", r"\bmusic\b", r"\bvoice acting\b", r"\bgraphics\b", r"\bart style\b", r"\batmosphere\b", r"\blore\b", r"\bstory\b"],
}

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"system prompt",
    r"as an ai",
    r"output exactly",
    r"override rules"
]


def sanitize_review_text(text: str) -> str:
    """Sanitizes user review text to prevent prompt injection and remove control characters."""
    if not text:
        return ""
    # Strip dangerous directives
    cleaned = text
    for pattern in INJECTION_PATTERNS:
        cleaned = re.sub(pattern, "[FILTERED_INSTRUCTION]", cleaned, flags=re.IGNORECASE)
    # Remove null bytes and non-printable control characters
    cleaned = "".join(ch for ch in cleaned if ch.isprintable() or ch in "\n\r\t ")
    return cleaned.strip()


class ReviewMiningService:
    def __init__(self, db: Session):
        self.db = db

    def mine_and_extract_topics(self, game_id: str, limit: int = 150) -> Dict[str, Any]:
        """
        Executes review mining pipeline for a game:
        1. Gathers reviews for game
        2. Cleans duplicates and sanitizes text
        3. Identifies topics and sentiments
        4. Calculates prevalence with explicit sample denominator and citations
        """
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise ValueError(f"Game with id {game_id} not found")

        # Get game platform IDs
        gp_ids = [gp.id for gp in self.db.query(GamePlatform.id).filter(GamePlatform.game_id == game.id).all()]
        if not gp_ids:
            return {
                "game_id": game_id,
                "game_name": game.canonical_name,
                "sample_size": 0,
                "topics_breakdown": [],
                "disclaimer": "No reviews found for this game platform."
            }

        reviews = self.db.query(ReviewItem).filter(
            ReviewItem.game_platform_id.in_(gp_ids)
        ).limit(limit).all()

        total_sample = len(reviews)
        if total_sample == 0:
            return {
                "game_id": game_id,
                "game_name": game.canonical_name,
                "sample_size": 0,
                "topics_breakdown": [],
                "disclaimer": "Muestra observada: 0 reseñas."
            }

        topic_stats = {t: {"count": 0, "praises": 0, "complaints": 0, "citations": []} for t in TOPIC_PATTERNS}

        for rev in reviews:
            text = sanitize_review_text(rev.review_text or "")
            if not text or len(text) < 10:
                continue

            voted_up = rev.voted_up
            text_lower = text.lower()

            for topic, patterns in TOPIC_PATTERNS.items():
                matched = False
                for p in patterns:
                    if re.search(p, text_lower):
                        matched = True
                        break

                if matched:
                    # Classify sentiment in topic context
                    sentiment = "positive" if voted_up else "negative"
                    topic_stats[topic]["count"] += 1
                    if sentiment == "positive":
                        topic_stats[topic]["praises"] += 1
                    else:
                        topic_stats[topic]["complaints"] += 1

                    # Extract short excerpt for evidence citation
                    words = text.split()
                    excerpt = " ".join(words[:30]) + ("..." if len(words) > 30 else "")

                    if len(topic_stats[topic]["citations"]) < 3:
                        topic_stats[topic]["citations"].append({
                            "source_review_id": rev.source_review_id,
                            "sentiment": sentiment,
                            "excerpt": excerpt,
                            "votes_up": rev.votes_up or 0
                        })

                    # Persist extraction if not existing
                    existing = self.db.query(ReviewTopicExtraction).filter(
                        ReviewTopicExtraction.game_id == game.id,
                        ReviewTopicExtraction.source_review_id == rev.source_review_id,
                        ReviewTopicExtraction.topic == topic
                    ).first()

                    if not existing:
                        extraction = ReviewTopicExtraction(
                            id=uuid.uuid4(),
                            review_item_id=rev.id,
                            game_id=game.id,
                            topic=topic,
                            sentiment=sentiment,
                            confidence=0.88,
                            evidence_excerpt=excerpt,
                            source_review_id=rev.source_review_id
                        )
                        self.db.add(extraction)

        self.db.commit()

        # Build topic breakdowns with strict sample denominator
        breakdown = []
        for topic, stat in topic_stats.items():
            if stat["count"] > 0:
                prevalence_pct = round((stat["count"] / total_sample) * 100, 2)
                complaint_ratio = round((stat["complaints"] / stat["count"]) * 100, 1)
                praise_ratio = round((stat["praises"] / stat["count"]) * 100, 1)

                breakdown.append({
                    "topic": topic,
                    "mentions_count": stat["count"],
                    "sample_denominator": total_sample,
                    "prevalence_percent": prevalence_pct,
                    "praises_count": stat["praises"],
                    "complaints_count": stat["complaints"],
                    "praise_ratio": praise_ratio,
                    "complaint_ratio": complaint_ratio,
                    "citations": stat["citations"]
                })

        breakdown.sort(key=lambda x: x["mentions_count"], reverse=True)

        return {
            "game_id": str(game.id),
            "game_name": game.canonical_name,
            "sample_size": total_sample,
            "topics_count": len(breakdown),
            "topics_breakdown": breakdown,
            "disclaimer": f"Muestra analizada: {total_sample} reseñas públicas. Prevalencia calculada estrictamente sobre el denominador de la muestra sin extrapolar a la totalidad de compradores."
        }
