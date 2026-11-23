from typing import Dict, Any, List
from app.config import settings

CONNECTORS_METADATA: List[Dict[str, Any]] = [
    {
        "provider_code": "steam_store",
        "provider_name": "Steam Store & Steamworks",
        "provider_type": "official_public",
        "status": "active",
        "capabilities": [
            "catalog",
            "metadata",
            "prices",
            "genres",
            "tags",
            "screenshots",
            "current_players",
            "reviews"
        ],
        "authentication": "api_key_or_public_endpoint",
        "terms_url": "https://partner.steamgames.com/doc/webapi_overview",
        "last_verified_at": None,
        "rate_limit_policy": "configurable",
        "supports_historical_data": False,
        "base_url": settings.STEAM_API_BASE_URL,
        "documentation_url": "https://partner.steamgames.com/doc/webapi"
    },
    {
        "provider_code": "steamspy",
        "provider_name": "SteamSpy",
        "provider_type": "third_party_public",
        "status": "active" if settings.STEAMSPY_ENABLED else "disabled",
        "capabilities": [
            "owner_estimates",
            "average_playtime",
            "recent_players"
        ],
        "authentication": "public_or_patreon_key",
        "terms_url": "https://steamspy.com/about",
        "last_verified_at": None,
        "rate_limit_policy": "1_req_per_second",
        "supports_historical_data": False,
        "base_url": "https://steamspy.com/api.php",
        "documentation_url": "https://steamspy.com/api.php"
    },
    {
        "provider_code": "igdb",
        "provider_name": "IGDB (Twitch)",
        "provider_type": "third_party_commercial",
        "status": "active" if settings.IGDB_ENABLED else "planned",
        "capabilities": [
            "metadata",
            "genres",
            "themes",
            "franchises",
            "platforms"
        ],
        "authentication": "oauth_client_credentials",
        "terms_url": "https://www.igdb.com/terms",
        "last_verified_at": None,
        "rate_limit_policy": "4_req_per_second",
        "supports_historical_data": False,
        "base_url": "https://api.igdb.com/v4",
        "documentation_url": "https://api-docs.igdb.com"
    },
    {
        "provider_code": "itch_io",
        "provider_name": "itch.io",
        "provider_type": "official_public",
        "status": "active" if settings.ITCH_ENABLED else "planned",
        "capabilities": [
            "public_discovery_rss",
            "creator_authorized_catalog"
        ],
        "authentication": "api_key_for_creator_or_none_for_rss",
        "terms_url": "https://itch.io/docs/api/overview",
        "last_verified_at": None,
        "rate_limit_policy": "standard",
        "supports_historical_data": False,
        "base_url": "https://itch.io",
        "documentation_url": "https://itch.io/docs/api/overview"
    },
    {
        "provider_code": "gog",
        "provider_name": "GOG",
        "provider_type": "official_public",
        "status": "planned",
        "capabilities": [
            "metadata_only",
            "prices"
        ],
        "authentication": "none",
        "terms_url": "https://docs.gog.com",
        "last_verified_at": None,
        "rate_limit_policy": "conservative",
        "supports_historical_data": False,
        "base_url": "https://gog.com",
        "documentation_url": "https://docs.gog.com"
    },
    {
        "provider_code": "epic_games",
        "provider_name": "Epic Games Store",
        "provider_type": "official_public",
        "status": "unavailable",
        "capabilities": [
            "metadata_only"
        ],
        "authentication": "none",
        "terms_url": "https://dev.epicgames.com",
        "last_verified_at": None,
        "rate_limit_policy": "conservative",
        "supports_historical_data": False,
        "base_url": "https://store.epicgames.com",
        "documentation_url": "https://dev.epicgames.com/documentation"
    },
    {
        "provider_code": "pcgamingwiki",
        "provider_name": "PCGamingWiki",
        "provider_type": "third_party_public",
        "status": "planned",
        "capabilities": [
            "technical_specs",
            "game_engines",
            "compatibility"
        ],
        "authentication": "none",
        "terms_url": "https://www.pcgamingwiki.com",
        "last_verified_at": None,
        "rate_limit_policy": "standard_mediawiki",
        "supports_historical_data": False,
        "base_url": "https://www.pcgamingwiki.com",
        "documentation_url": "https://www.pcgamingwiki.com/wiki/PCGamingWiki:API"
    }
]


def get_connector_metadata(provider_code: str) -> Dict[str, Any]:
    for conn in CONNECTORS_METADATA:
        if conn["provider_code"] == provider_code:
            return conn
    raise ValueError(f"Unknown provider: {provider_code}")
