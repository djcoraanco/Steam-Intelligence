from app.core.database import Base
from app.models.catalog import (
    Platform,
    Game,
    GamePlatform,
    Organization,
    GameDeveloper,
    GamePublisher,
    TaxonomyItem,
    GameTaxonomy,
)
from app.models.sources import DataSource, RawPayload
from app.models.snapshots import (
    PlayerSnapshot,
    PriceSnapshot,
    ReviewSnapshot,
    RankingSnapshot,
    ReviewItem,
)
from app.models.rollups import GameMetricRollup, MarketSegmentRollup
from app.models.research import (
    TrendSignal,
    NicheOpportunity,
    ResearchProject,
    ResearchRun,
    ResearchResult,
)
from app.models.user import User, Role, UserRole, AuditLog
from app.models.checkpoints import IngestionCheckpoint
from app.models.competitors import GameCompetitor, ReviewTopicExtraction
from app.models.cross_references import GameCrossReference
from app.models.events import IndustryEvent

__all__ = [
    "Base",
    "Platform",
    "Game",
    "GamePlatform",
    "Organization",
    "GameDeveloper",
    "GamePublisher",
    "TaxonomyItem",
    "GameTaxonomy",
    "DataSource",
    "RawPayload",
    "PlayerSnapshot",
    "PriceSnapshot",
    "ReviewSnapshot",
    "RankingSnapshot",
    "ReviewItem",
    "GameMetricRollup",
    "MarketSegmentRollup",
    "TrendSignal",
    "NicheOpportunity",
    "ResearchProject",
    "ResearchRun",
    "ResearchResult",
    "User",
    "Role",
    "UserRole",
    "AuditLog",
    "IngestionCheckpoint",
    "GameCompetitor",
    "ReviewTopicExtraction",
    "GameCrossReference",
    "IndustryEvent",
]
