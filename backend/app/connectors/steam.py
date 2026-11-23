from typing import Dict, Any, Optional
import httpx
from app.config import settings
from app.connectors.base import BaseConnector
from app.core.logging import logger


class SteamConnector(BaseConnector):
    """
    Connector for Steamworks Web API & Steam Storefront.
    Strictly adheres to documented endpoints and contracts:
    - IStoreService/GetAppList/v1
    - /api/appdetails
    - ISteamUserStats/GetNumberOfCurrentPlayers/v1
    - IUserReviewsService/GetAppReviews/v1
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            provider_code="steam_store",
            base_url=settings.STEAM_API_BASE_URL,
            timeout=20.0
        )
        self.api_key = api_key or settings.STEAM_WEB_API_KEY
        self.storefront_base_url = settings.STEAM_STORE_BASE_URL.rstrip("/")

    def get_capabilities(self) -> list[str]:
        return [
            "catalog",
            "metadata",
            "prices",
            "genres",
            "tags",
            "screenshots",
            "current_players",
            "reviews"
        ]

    async def get_app_list(
        self,
        last_appid: Optional[int] = None,
        max_results: int = 10000,
        if_modified_since: Optional[int] = None,
        include_games: bool = True,
        include_dlc: bool = False
    ) -> Dict[str, Any]:
        """IStoreService/GetAppList/v1/"""
        params: Dict[str, Any] = {
            "max_results": min(max_results, 50000),
            "include_games": str(include_games).lower(),
            "include_dlc": str(include_dlc).lower()
        }
        if self.api_key:
            params["key"] = self.api_key
        if last_appid is not None:
            params["last_appid"] = last_appid
        if if_modified_since is not None:
            params["if_modified_since"] = if_modified_since

        resp = await self._get("IStoreService/GetAppList/v1/", params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_app_details(
        self,
        appid: int,
        country_code: str = "us",
        language: str = "english"
    ) -> Dict[str, Any]:
        """Storefront /api/appdetails"""
        url = f"{self.storefront_base_url}/api/appdetails"
        params = {
            "appids": appid,
            "cc": country_code,
            "l": language
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data

    async def get_number_of_current_players(self, appid: int) -> Dict[str, Any]:
        """ISteamUserStats/GetNumberOfCurrentPlayers/v1/"""
        params = {"appid": appid}
        if self.api_key:
            params["key"] = self.api_key
        resp = await self._get("ISteamUserStats/GetNumberOfCurrentPlayers/v1/", params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_app_reviews(
        self,
        appid: int,
        cursor: str = "*",
        language: str = "all",
        filter_type: str = "recent",
        num_per_page: int = 100
    ) -> Dict[str, Any]:
        """IUserReviewsService/GetAppReviews/v1/"""
        params = {
            "json": 1,
            "appid": appid,
            "cursor": cursor,
            "language": language,
            "filter": filter_type,
            "num_per_page": min(num_per_page, 100)
        }
        if self.api_key:
            params["key"] = self.api_key
        resp = await self._get("IUserReviewsService/GetAppReviews/v1/", params=params)
        resp.raise_for_status()
        return resp.json()
