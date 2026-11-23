from typing import Dict, Any, Optional
import httpx
from app.connectors.base import BaseConnector
from app.core.logging import logger


class SteamSpyConnector(BaseConnector):
    """
    Asynchronous connector for SteamSpy API.
    Conforms to the protocol popularized by steamspypi:
    - request=top100in2weeks
    - request=top100forever
    - request=top100owned
    - request=appdetails&appid={appid}
    - request=genre&genre={genre}
    - request=tag&tag={tag}
    - request=all&page={page}
    """

    def __init__(self, base_url: str = "https://steamspy.com/api.php", timeout: float = 15.0):
        super().__init__(
            provider_code="steamspy",
            base_url=base_url,
            timeout=timeout
        )

    def get_capabilities(self) -> list[str]:
        return [
            "owner_estimates",
            "average_playtime",
            "recent_players",
            "top100",
            "tag_discovery"
        ]

    async def download(self, data_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic query interface compatible with steamspypi.download(data_request).
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SteamIntelligence/1.0 (steamspypi-compatible)"
        }
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers=headers) as client:
            resp = await client.get(self.base_url, params=data_request)
            resp.raise_for_status()
            return resp.json()

    async def get_app_details(self, appid: int) -> Dict[str, Any]:
        """Fetch SteamSpy estimates for a specific AppID."""
        return await self.download({"request": "appdetails", "appid": str(appid)})

    async def get_top100_in_2weeks(self) -> Dict[str, Any]:
        """Fetch top 100 games by player count in the last 2 weeks."""
        return await self.download({"request": "top100in2weeks"})

    async def get_top100_forever(self) -> Dict[str, Any]:
        """Fetch top 100 games played since March 2009."""
        return await self.download({"request": "top100forever"})

    async def get_top100_owned(self) -> Dict[str, Any]:
        """Fetch top 100 games sorted by estimated number of owners."""
        return await self.download({"request": "top100owned"})

    async def get_by_genre(self, genre: str) -> Dict[str, Any]:
        """Fetch games in a given genre."""
        return await self.download({"request": "genre", "genre": genre})

    async def get_by_tag(self, tag: str) -> Dict[str, Any]:
        """Fetch games with a given Steam community tag."""
        return await self.download({"request": "tag", "tag": tag})

    async def get_all(self, page: int = 0) -> Dict[str, Any]:
        """
        Fetch 1000 games per page.
        Note: SteamSpy enforces a rate-limit of 1 'all' request per minute.
        """
        return await self.download({"request": "all", "page": str(page)})
