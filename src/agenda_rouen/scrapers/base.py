"""Base scraper interface."""

from __future__ import annotations

import abc
import asyncio
import logging

import httpx

from agenda_rouen.models import RawEvent

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS = {502, 503, 504, 429}
_MAX_RETRIES = 3
_BACKOFF_BASE = 1.5  # seconds — 1.5, 3, 6


class BaseScraper(abc.ABC):
    """All scrapers must implement this interface."""

    name: str  # unique identifier, e.g. "rouen_on_est"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            headers={"User-Agent": "AgendaRouen/0.1 (+https://github.com/agenda-rouen)"},
        )

    async def __aenter__(self) -> BaseScraper:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self._client.aclose()

    async def _get(
        self,
        url: str,
        *,
        params: dict[str, str | int] | list[tuple[str, str | int]] | None = None,
    ) -> httpx.Response:
        """HTTP GET with exponential backoff on transient errors (502/503/504/429)."""
        last_exc: Exception | None = None

        for attempt in range(_MAX_RETRIES + 1):
            try:
                resp = await self._client.get(url, params=params)
            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt < _MAX_RETRIES:
                    wait = _BACKOFF_BASE * (2 ** attempt)
                    logger.warning(
                        "%s: timeout on %s, retrying in %.1fs (%d/%d)",
                        self.name, url[:80], wait, attempt + 1, _MAX_RETRIES,
                    )
                    await asyncio.sleep(wait)
                    continue
                raise

            if resp.status_code not in _RETRYABLE_STATUS or attempt == _MAX_RETRIES:
                return resp

            # Respect Retry-After header if present
            retry_after = resp.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                wait = min(float(retry_after), 30.0)
            else:
                wait = _BACKOFF_BASE * (2 ** attempt)

            logger.warning(
                "%s: HTTP %d on %s, retrying in %.1fs (%d/%d)",
                self.name, resp.status_code, url[:80], wait, attempt + 1, _MAX_RETRIES,
            )
            await asyncio.sleep(wait)

        # Should not reach here, but satisfy the type checker
        assert last_exc is not None
        raise last_exc

    @abc.abstractmethod
    async def scrape(self) -> list[RawEvent]:
        """Scrape events from the source and return raw events."""
        ...
