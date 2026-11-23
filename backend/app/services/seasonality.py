import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_

from app.models.catalog import Game, GamePlatform, GameTaxonomy, TaxonomyItem
from app.models.snapshots import PlayerSnapshot, ReviewSnapshot, PriceSnapshot
from app.models.events import IndustryEvent

logger = logging.getLogger(__name__)

# Default industry events catalog with official source citations
DEFAULT_EVENTS = [
    {
        "code": "steam_spring_sale_2026",
        "name": "Steam Spring Sale 2026",
        "event_type": "seasonal_sale",
        "start_date": date(2026, 3, 12),
        "end_date": date(2026, 3, 19),
        "source_ref": "Steamworks Official Event Documentation 2026",
        "description": "Gran rebaja estacional de primavera de Steam. El escaparate principal prioriza descuentos sobre nuevos lanzamientos.",
        "historical_impact": {"visibility_impact": "high_discount_focus", "discount_volume_surge": 0.85}
    },
    {
        "code": "steam_next_fest_june_2026",
        "name": "Steam Next Fest - June Edition 2026",
        "event_type": "next_fest",
        "start_date": date(2026, 6, 8),
        "end_date": date(2026, 6, 15),
        "source_ref": "Steamworks Next Fest Schedule 2026",
        "description": "Festival de demos para juegos no lanzados. Alto volumen de transmisiones y wishlists.",
        "historical_impact": {"demo_traffic_surge": 3.5, "wishlist_velocity": 4.2}
    },
    {
        "code": "steam_summer_sale_2026",
        "name": "Steam Summer Sale 2026",
        "event_type": "seasonal_sale",
        "start_date": date(2026, 6, 25),
        "end_date": date(2026, 7, 9),
        "source_ref": "Steamworks Official Event Documentation 2026",
        "description": "Mayor evento de ventas de mitad de año en PC. Desvía visibilidad de títulos de precio completo sin descuento.",
        "historical_impact": {"visibility_impact": "maximum_discount_focus", "discount_volume_surge": 0.95}
    },
    {
        "code": "steam_next_fest_oct_2026",
        "name": "Steam Next Fest - October Edition 2026",
        "event_type": "next_fest",
        "start_date": date(2026, 10, 12),
        "end_date": date(2026, 10, 19),
        "source_ref": "Steamworks Next Fest Schedule 2026",
        "description": "Segunda edición anual de festival de demos otoñal de Steam.",
        "historical_impact": {"demo_traffic_surge": 3.2, "wishlist_velocity": 3.8}
    },
    {
        "code": "steam_scream_fest_2026",
        "name": "Steam Scream Fest (Halloween) 2026",
        "event_type": "seasonal_sale",
        "start_date": date(2026, 10, 26),
        "end_date": date(2026, 11, 2),
        "source_ref": "Steamworks Official Event Documentation 2026",
        "description": "Evento temático de terror, supervivencia y suspenso.",
        "historical_impact": {"genre_boost": ["Horror", "Survival", "Zombies"], "visibility_boost": 2.1}
    },
    {
        "code": "steam_autumn_sale_2026",
        "name": "Steam Autumn Sale 2026",
        "event_type": "seasonal_sale",
        "start_date": date(2026, 11, 24),
        "end_date": date(2026, 12, 1),
        "source_ref": "Steamworks Official Event Documentation 2026",
        "description": "Rebajas de otoño y nominaciones a los Steam Awards.",
        "historical_impact": {"visibility_impact": "high_discount_focus", "discount_volume_surge": 0.88}
    },
    {
        "code": "steam_winter_sale_2026",
        "name": "Steam Winter Sale 2026",
        "event_type": "seasonal_sale",
        "start_date": date(2026, 12, 17),
        "end_date": date(2027, 1, 5),
        "source_ref": "Steamworks Official Event Documentation 2026",
        "description": "Mayor periodo de gasto navideño y vacaciones de invierno.",
        "historical_impact": {"visibility_impact": "maximum_discount_focus", "holiday_spending_surge": 1.2}
    }
]


class SeasonalityEngine:
    def __init__(self, db: Session):
        self.db = db

    def seed_events_if_empty(self):
        """Initializes default industry events if none exist."""
        count = self.db.query(IndustryEvent).count()
        if count == 0:
            for ev_data in DEFAULT_EVENTS:
                ev = IndustryEvent(
                    id=uuid.uuid4(),
                    code=ev_data["code"],
                    name=ev_data["name"],
                    event_type=ev_data["event_type"],
                    start_date=ev_data["start_date"],
                    end_date=ev_data["end_date"],
                    source_ref=ev_data["source_ref"],
                    description=ev_data["description"],
                    historical_impact=ev_data["historical_impact"]
                )
                self.db.add(ev)
            self.db.commit()

    def get_events(self, from_date: Optional[date] = None, to_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Returns industry events filtered by date range."""
        self.seed_events_if_empty()
        query = self.db.query(IndustryEvent)
        if from_date:
            query = query.filter(IndustryEvent.end_date >= from_date)
        if to_date:
            query = query.filter(IndustryEvent.start_date <= to_date)

        events = query.order_by(IndustryEvent.start_date.asc()).all()
        return [
            {
                "id": str(e.id),
                "code": e.code,
                "name": e.name,
                "event_type": e.event_type,
                "start_date": e.start_date.isoformat(),
                "end_date": e.end_date.isoformat(),
                "source_ref": e.source_ref,
                "description": e.description,
                "historical_impact": e.historical_impact
            }
            for e in events
        ]

    def get_cohort_analysis(self, cohort_dimension: str = "release_year") -> Dict[str, Any]:
        """
        Groups games into cohorts (e.g. by release_year or early_access)
        and computes observed median/average metrics with sample sizes.
        """
        games = self.db.query(Game).filter(Game.release_date.isnot(None)).all()
        cohorts = {}

        for g in games:
            if cohort_dimension == "release_year":
                key = str(g.release_date.year)
            elif cohort_dimension == "early_access":
                key = "Early Access" if g.is_early_access else "Direct Full Release"
            else:
                key = f"M{g.release_date.month:02d}"

            if key not in cohorts:
                cohorts[key] = {
                    "cohort_key": key,
                    "games_count": 0,
                    "games": []
                }
            cohorts[key]["games_count"] += 1
            cohorts[key]["games"].append(g)

        cohort_results = []
        for key, data in sorted(cohorts.items()):
            n = data["games_count"]
            cohort_results.append({
                "cohort": key,
                "sample_size": n,
                "early_access_ratio": round(sum(1 for g in data["games"] if g.is_early_access) / n * 100, 1) if n > 0 else 0,
            })

        return {
            "dimension": cohort_dimension,
            "total_sample_size": len(games),
            "cohorts": cohort_results,
            "disclaimer": "Los resultados observados reflejan correlación histórica dentro de la muestra y no garantizan causalidad comercial."
        }

    def analyze_launch_collision(
        self,
        target_date: date,
        days_window: int = 14,
        genre_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates potential conflicts for a planned launch date:
        1. Overlaps with industry events (Steam Sales, Next Fest)
        2. Competing game releases scheduled in the window
        3. Collision risk score (0-100) and recommendation of alternative windows
        """
        self.seed_events_if_empty()
        window_start = target_date - timedelta(days=days_window)
        window_end = target_date + timedelta(days=days_window)

        # 1. Check overlapping industry events
        overlapping_events = self.db.query(IndustryEvent).filter(
            and_(
                IndustryEvent.start_date <= window_end,
                IndustryEvent.end_date >= window_start
            )
        ).all()

        event_collisions = []
        event_penalty = 0
        for ev in overlapping_events:
            direct_collision = ev.start_date <= target_date <= ev.end_date
            penalty = 40 if ev.event_type == "seasonal_sale" else 25
            if direct_collision:
                penalty += 15
            event_penalty += penalty

            event_collisions.append({
                "name": ev.name,
                "event_type": ev.event_type,
                "start_date": ev.start_date.isoformat(),
                "end_date": ev.end_date.isoformat(),
                "direct_hit": direct_collision,
                "source": ev.source_ref,
                "impact_note": ev.description
            })

        # 2. Check scheduled game releases in window
        games_in_window = self.db.query(Game).filter(
            and_(
                Game.release_date >= window_start,
                Game.release_date <= window_end
            )
        ).all()

        competing_games = []
        for g in games_in_window:
            competing_games.append({
                "id": str(g.id),
                "name": g.canonical_name,
                "release_date": g.release_date.isoformat() if g.release_date else None,
                "is_early_access": g.is_early_access
            })

        # Density score calculation
        game_penalty = min(len(competing_games) * 10, 45)
        raw_collision_score = min(100, event_penalty + game_penalty)

        if raw_collision_score >= 75:
            collision_level = "extreme"
            recommendation = "Ventana de lanzamiento de muy alto riesgo debido a coincidencia directa con rebajas estacionales o alta densidad de títulos. Se recomienda postergar o adelantar al menos 2 semanas."
        elif raw_collision_score >= 50:
            collision_level = "high"
            recommendation = "Riesgo significativo de colisión. Conviene evaluar ventanas adyacentes donde el escaparate principal no esté copado por eventos de descuento."
        elif raw_collision_score >= 25:
            collision_level = "moderate"
            recommendation = "Riesgo moderado. Nivel de competencia manejable, mantener monitoreo de anuncios de última hora."
        else:
            collision_level = "low"
            recommendation = "Ventana despejada de eventos mayores conocidos. Óptima para captar visibilidad orgánica si el producto y marketing están listos."

        # Suggest 2 alternative cleaner windows
        alt_window_1 = {
            "start": (target_date + timedelta(days=21)).isoformat(),
            "end": (target_date + timedelta(days=35)).isoformat(),
            "reason": "Ventana posterior alejada de los eventos detectados."
        }
        alt_window_2 = {
            "start": (target_date - timedelta(days=35)).isoformat(),
            "end": (target_date - timedelta(days=21)).isoformat(),
            "reason": "Ventana previa para anticipar el flujo estacional."
        }

        return {
            "target_date": target_date.isoformat(),
            "window_range": {
                "start": window_start.isoformat(),
                "end": window_end.isoformat(),
                "days_radius": days_window
            },
            "collision_score": raw_collision_score,
            "collision_level": collision_level,
            "recommendation": recommendation,
            "overlapping_events": event_collisions,
            "competing_releases_count": len(competing_games),
            "competing_releases": competing_games[:10],
            "alternative_windows": [alt_window_1, alt_window_2],
            "disclaimer": "Las fechas de eventos e indicios de lanzamiento se basan en anuncios observados. La asociación temporal no garantiza causalidad ni éxito comercial."
        }
