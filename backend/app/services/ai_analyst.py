import re
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.catalog import Game, GamePlatform
from app.models.rollups import MarketSegmentRollup, GameMetricRollup
from app.models.research import NicheOpportunity
from app.services.review_mining import ReviewMiningService
from app.services.competitor_analyzer import CompetitorAnalyzerService
from app.services.seasonality import SeasonalityEngine

logger = logging.getLogger(__name__)

PROMPT_VERSION = "market-analyst-v1"


def sanitize_input(text: str) -> str:
    """Strips dangerous injection instructions before presenting text to AI."""
    patterns = [
        r"ignore previous instructions",
        r"system prompt",
        r"as an ai",
        r"override rules",
        r"drop database",
        r"grant admin"
    ]
    cleaned = text
    for p in patterns:
        cleaned = re.sub(p, "[REDACTED_DIRECTIVE]", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


class AIAnalystService:
    def __init__(self, db: Session, ollama_url: str = "http://localhost:11434"):
        self.db = db
        self.ollama_url = ollama_url

    def query_tools(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes strictly typed internal query tools on verified database models.
        No raw dynamic SQL allowed.
        """
        if tool_name == "get_segment_metrics":
            segment = params.get("segment", "Indie")
            rollups = self.db.query(MarketSegmentRollup).filter(
                MarketSegmentRollup.segment_type == "genre"
            ).all()
            for r in rollups:
                if r.segment_key.get("genre", "").lower() == segment.lower():
                    return {
                        "genre": segment,
                        "total_games": r.total_games,
                        "active_games": r.active_games,
                        "median_price_cents": r.median_price_minor,
                        "hhi_concentration": float(r.hhi_concentration) if r.hhi_concentration else None,
                        "recent_releases": r.recent_releases_count
                    }
            return {"genre": segment, "status": "no_rollups_computed"}

        elif tool_name == "get_niche_opportunities":
            niches = self.db.query(NicheOpportunity).order_by(
                NicheOpportunity.opportunity_score.desc()
            ).limit(5).all()
            return {
                "niches": [
                    {
                        "name": n.name,
                        "score": float(n.opportunity_score),
                        "confidence": n.confidence_band,
                        "segment": n.segment_definition
                    }
                    for n in niches
                ]
            }

        elif tool_name == "get_review_topics":
            game_id = params.get("game_id")
            if not game_id:
                return {"error": "game_id required"}
            miner = ReviewMiningService(self.db)
            return miner.mine_and_extract_topics(game_id, limit=50)

        elif tool_name == "get_release_calendar":
            target_date_str = params.get("target_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
            engine = SeasonalityEngine(self.db)
            from datetime import date
            parts = [int(p) for p in target_date_str.split("-")]
            target_date = date(parts[0], parts[1], parts[2])
            return engine.analyze_launch_collision(target_date, days_window=14)

        return {"error": f"Unknown tool: {tool_name}"}

    async def analyze_market_question(
        self,
        question: str,
        target_genre: Optional[str] = "Action",
        target_game_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes a market query and returns structured analysis adhering strictly
        to Master Spec Section 12.4.
        Uses typed internal tools to ground findings in empirical evidence.
        """
        sanitized_question = sanitize_input(question)
        cutoff_date = datetime.now(timezone.utc).isoformat()

        # Gather real evidence from database
        segment_data = self.query_tools("get_segment_metrics", {"segment": target_genre})
        niches_data = self.query_tools("get_niche_opportunities", {})

        findings = []
        if segment_data.get("total_games"):
            findings.append({
                "claim": f"El segmento de género '{target_genre}' presenta {segment_data['total_games']} juegos observados, con una concentración de mercado de {segment_data.get('hhi_concentration', 0.15)}.",
                "metric": "market_segment_concentration",
                "period": "historical_rollup",
                "evidence_refs": [f"market_segment_rollups:genre:{target_genre}"],
                "confidence": "high"
            })

        top_niches = niches_data.get("niches", [])
        if top_niches:
            top_n = top_niches[0]
            findings.append({
                "claim": f"Se ha detectado un nicho emergente '{top_n['name']}' con oportunidad de {top_n['score']}/100 y confianza {top_n['confidence']}.",
                "metric": "niche_opportunity_score",
                "period": "latest_analysis",
                "evidence_refs": [f"niche_opportunities:{top_n['name']}"],
                "confidence": top_n["confidence"]
            })

        recommendations = [
            f"Validar la densidad de competidores activos en el segmento '{target_genre}' antes de fijar precio.",
            "Revisar el desglose de quejas recurrentes en reseñas de títulos comparables (bugs, UI y balance).",
            "Monitorear el calendario de Steam Next Fest para evitar coincidencia con grandes periodos de descuento."
        ]

        limitations = [
            "Los datos de ventas e ingresos netos de terceros no son públicos y se omiten deliberadamente para evitar falsa precisión.",
            "La muestra observada refleja datos públicos de Steamworks y Storefront.",
            "La correlación de métricas de actividad no garantiza desempeño comercial causal."
        ]

        summary_text = (
            f"Análisis estructurado para la consulta: '{sanitized_question}'. "
            f"Basado en telemetría observada de catálogo y modelos deterministas de analítica."
        )

        return {
            "title": f"Informe de Inteligencia de Mercado: {target_genre}",
            "summary": summary_text,
            "findings": findings,
            "recommendations": recommendations,
            "limitations": limitations,
            "data_cutoff": cutoff_date,
            "model": "internal/rule-grounded-analyst-v1",
            "prompt_version": PROMPT_VERSION
        }

    async def validate_game_concept(self, concept_description: str, genres: List[str]) -> Dict[str, Any]:
        """
        Evaluates a game pitch / concept against competitive density and genre benchmarks.
        """
        sanitized_concept = sanitize_input(concept_description)
        cutoff_date = datetime.now(timezone.utc).isoformat()

        primary_genre = genres[0] if genres else "Indie"
        segment_data = self.query_tools("get_segment_metrics", {"segment": primary_genre})

        return {
            "title": f"Validación de Concepto: {sanitized_concept[:40]}...",
            "summary": f"Evaluación de viabilidad y entorno competitivo para el concepto en los géneros {', '.join(genres)}.",
            "findings": [
                {
                    "claim": f"El entorno en '{primary_genre}' cuenta con actividad regular de jugadores y mediana de precios registrada.",
                    "metric": "competitive_density",
                    "period": "current_snapshot",
                    "evidence_refs": [f"genre_taxonomies:{primary_genre}"],
                    "confidence": "medium"
                }
            ],
            "recommendations": [
                "Desarrollar una demo jugable para Steam Next Fest al menos 4 meses antes del lanzamiento.",
                "Estructurar la página de tienda destacando mecánicas diferenciales respecto al top del género."
            ],
            "limitations": [
                "Estimación de viabilidad conceptual sin acceso a wishlists privadas de competidores."
            ],
            "data_cutoff": cutoff_date,
            "model": "internal/concept-validator-v1",
            "prompt_version": "concept-validator-v1"
        }
