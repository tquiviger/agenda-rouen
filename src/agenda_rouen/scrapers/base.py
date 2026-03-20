"""Base scraper interface."""

from __future__ import annotations

import abc

import httpx

from agenda_rouen.models import RawEvent


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

    @abc.abstractmethod
    async def scrape(self) -> list[RawEvent]:
        """Scrape events from the source and return raw events."""
        ...
