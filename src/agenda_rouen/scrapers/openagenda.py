"""Scraper for OpenAgenda-powered agendas (Métropole, Ville de Rouen, Bibliothèques)."""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime, timedelta

from agenda_rouen.models import RawEvent
from agenda_rouen.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

# OpenAgenda v2 JSON export — no API key required
_BASE_URL = "https://openagenda.com/agendas/{uid}/events.v2.json"
_PAGE_SIZE = 100
_MAX_PAGES = 50  # Safety limit to prevent infinite pagination loops

# Known Rouen-area agendas
AGENDAS: dict[str, int] = {
    "openagenda_metropole": 11362982,
    "openagenda_rouen": 11174431,
    "openagenda_bibliotheques": 8049538,
}


class OpenAgendaScraper(BaseScraper):
    """Scraper for a single OpenAgenda agenda."""

    name: str  # set per instance

    def __init__(
        self,
        agenda_name: str,
        agenda_uid: int,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self.name = agenda_name
        self._uid = agenda_uid

    async def scrape(self) -> list[RawEvent]:
        events: list[RawEvent] = []
        after: list[str] | None = None

        now = datetime.now(UTC)
        time_min = now.strftime("%Y-%m-%dT%H:%M:%S%z")
        time_max = (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S%z")

        for _page in range(1, _MAX_PAGES + 1):
            params: list[tuple[str, str | int]] = [
                ("detailed", 1),
                ("limit", _PAGE_SIZE),
                ("monolingual", "fr"),
                ("timings[gte]", time_min),
                ("timings[lte]", time_max),
            ]
            if after is not None:
                for val in after:
                    params.append(("after[]", val))

            url = _BASE_URL.format(uid=self._uid)
            resp = await self._get(url, params=params)
            resp.raise_for_status()
            try:
                data = resp.json()
            except Exception:
                logger.error("OpenAgenda [%s]: invalid JSON response", self.name)
                break

            for raw in data.get("events", []):
                event = _parse_event(raw, source=self.name)
                if event is not None:
                    events.append(event)

            # Cursor-based pagination: "sort" field is the cursor for next page
            fetched = data.get("events", [])
            if len(fetched) < _PAGE_SIZE:
                break

            after = data.get("sort")
            if not after:
                break
        else:
            logger.warning(
                "OpenAgenda [%s]: hit max page limit (%d), stopping", self.name, _MAX_PAGES,
            )

        logger.info("OpenAgenda [%s]: fetched %d events", self.name, len(events))
        return events


def _parse_event(raw: dict, source: str) -> RawEvent | None:
    """Parse a single OpenAgenda event into a RawEvent."""
    title = _get_fr(raw.get("title"))
    if not title:
        return None

    # Timings
    first = raw.get("firstTiming") or {}
    last = raw.get("lastTiming") or {}
    date_start = _parse_date(first.get("begin"))
    if date_start is None:
        return None

    date_end = _parse_date(last.get("end"))

    # Time from first timing
    time_str = ""
    begin = first.get("begin", "")
    if "T" in begin:
        time_str = begin.split("T")[1][:5]  # "HH:MM"

    # Location
    loc = raw.get("location") or {}
    location_name = loc.get("name", "")
    address_parts = [loc.get("address", ""), loc.get("postalCode", ""), loc.get("city", "")]
    address = ", ".join(p for p in address_parts if p)

    # Image — filter out placeholder URLs like "https://cdn.openagenda.com/main/"
    image = raw.get("image") or {}
    image_base = image.get("base", "")
    image_url = image_base if image_base and not image_base.endswith("/main/") else ""

    # URL: prefer registration link, then links[], fall back to empty
    # Ignore mailto: entries — they are contact emails, not navigable URLs
    event_url = ""
    for reg in raw.get("registration", []):
        value = reg.get("value", "")
        if reg.get("type") == "link" and value and not value.startswith("mailto:"):
            event_url = value
            break
    if not event_url:
        for link in raw.get("links", []):
            value = link.get("link", "")
            if value and not value.startswith("mailto:"):
                event_url = value
                break

    # Description
    description = _get_fr(raw.get("description"))

    return RawEvent(
        title=title,
        description=description,
        date_start=date_start,
        date_end=date_end,
        time=time_str,
        location=location_name,
        address=address,
        url=event_url,
        image_url=image_url,
        source=source,
        raw_category="",
    )


def _get_fr(value: dict | str | None) -> str:
    """Extract French text from an OpenAgenda multilingual field."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return value.get("fr", "") or ""


def _parse_date(value: str | None) -> date | None:
    """Parse an ISO datetime string into a date."""
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def create_openagenda_scrapers() -> list[OpenAgendaScraper]:
    """Create scraper instances for all known OpenAgenda agendas."""
    return [
        OpenAgendaScraper(agenda_name=name, agenda_uid=uid)
        for name, uid in AGENDAS.items()
    ]
