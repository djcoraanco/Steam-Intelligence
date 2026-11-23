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
        "authentication": "public_or_api_key",
        "terms_url": "https://partner.steamgames.com/doc/webapi_overview",
        "last_verified_at": None,
        "rate_limit_policy": "standard_steam",
        "supports_historical_data": False,
        "base_url": settings.STEAM_API_BASE_URL,
        "documentation_url": "https://partner.steamgames.com/doc/webapi"
    },
    {
        "provider_code": "steamspy",
        "provider_name": "SteamSpy",
        "provider_type": "third_party_public",
        "status": "active",
        "capabilities": [
            "owner_estimates",
            "average_playtime",
            "recent_players"
        ],
        "authentication": "public_api",
        "terms_url": "https://steamspy.com/about",
        "last_verified_at": None,
        "rate_limit_policy": "1_req_per_second",
        "supports_historical_data": False,
        "base_url": "https://steamspy.com/api.php",
        "documentation_url": "https://steamspy.com/api.php"
    },
    {
        "provider_code": "itch_io",
        "provider_name": "itch.io",
        "provider_type": "official_public",
        "status": "active",
        "capabilities": [
            "public_discovery_rss",
            "new_releases_feed",
            "featured_games"
        ],
        "authentication": "public_rss_feed",
        "terms_url": "https://itch.io/docs/api/overview",
        "last_verified_at": None,
        "rate_limit_policy": "standard_rss",
        "supports_historical_data": False,
        "base_url": "https://itch.io",
        "documentation_url": "https://itch.io/docs/api/overview"
    },
    {
        "provider_code": "gog",
        "provider_name": "GOG",
        "provider_type": "official_store_public",
        "status": "active",
        "capabilities": [
            "catalog_discovery",
            "metadata_only",
            "store_links"
        ],
        "authentication": "none",
        "terms_url": "https://docs.gog.com",
        "last_verified_at": None,
        "rate_limit_policy": "conservative",
        "supports_historical_data": False,
        "base_url": "https://catalog.gog.com",
        "documentation_url": "https://docs.gog.com"
    },
    {
        "provider_code": "epic_games",
        "provider_name": "Epic Games Store",
        "provider_type": "official_store_public",
        "status": "active",
        "capabilities": [
            "public_promotions",
            "metadata_only",
            "store_links"
        ],
        "authentication": "none",
        "terms_url": "https://dev.epicgames.com",
        "last_verified_at": None,
        "rate_limit_policy": "conservative",
        "supports_historical_data": False,
        "base_url": "https://store-site-backend-static-ipv4.ak.epicgames.com",
        "documentation_url": "https://dev.epicgames.com/documentation"
    },
    {
        "provider_code": "pcgamingwiki",
        "provider_name": "PCGamingWiki",
        "provider_type": "third_party_public",
        "status": "active",
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
    },
    {
        "provider_code": "igdb",
        "provider_name": "IGDB (Twitch)",
        "provider_type": "third_party_commercial",
        "status": "active" if settings.IGDB_CLIENT_ID else "unconfigured",
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
    }
]


def get_connector_metadata(provider_code: str) -> Dict[str, Any]:
    for conn in CONNECTORS_METADATA:
        if conn["provider_code"] == provider_code:
            return conn
    raise ValueError(f"Unknown provider: {provider_code}")
