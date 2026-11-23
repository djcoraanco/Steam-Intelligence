from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from app.core.logging import logger


class BaseConnector(ABC):
    def __init__(self, provider_code: str, base_url: str, timeout: float = 15.0):
        self.provider_code = provider_code
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """Return the list of validated capabilities for this provider."""
        pass

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                return response
            except httpx.HTTPError as exc:
                logger.error("connector_http_error", provider=self.provider_code, url=url, error=str(exc))
                raise
