"""Scraper for rouenonest.fr via Google Calendar API.

RouenOnEst embeds 6 public Google Calendars. We fetch events directly
from the Google Calendar API rather than scraping HTML.
"""

from __future__ import annotations

import logging
import os
import re
from datetime import UTC, date, datetime, timedelta

from agenda_rouen.models import RawEvent
from agenda_rouen.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

_GCAL_API = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"

# Regex to extract time from titles like "Event (20h)" or "Event (20h30)"
_TIME_IN_TITLE_RE = re.compile(r"\s*\((\d{1,2})h(\d{2})?\)\s*$")

_SPORTS_CATEGORY = "Sports & Compétitions"

# Calendar ID → human-readable category label
CALENDARS: dict[str, str] = {
    "rouenonest@gmail.com": "Grands événements",
    "125b957941466178d3cf24efd398d9fc8eb4e97c59253adcf3cc040fe28a51e5"
    "@group.calendar.google.com": "Animations & Spectacles",
    "5bf0dd85e236b8d28acc0e48cb5ea7f62c5ed1478d71eb8b1cf91412658d85ad"
    "@group.calendar.google.com": "Culture & Expos",
    "73790b160dc92784b114778740653d61f30543daedc382c496b27e93f4c1f232"
    "@group.calendar.google.com": "Dates majeures",
    "e5524612dc9f81327323b67f75eba260b28a3994a1deae5f2412a99b5760065d"
    "@group.calendar.google.com": "Sports & Compétitions",
}


class RouenOnEstScraper(BaseScraper):
    name = "rouen_on_est"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._api_key = os.environ.get("GOOGLE_CALENDAR_API_KEY", "")

    async def scrape(self) -> list[RawEvent]:
        if not self._api_key:
            logger.warning("GOOGLE_CALENDAR_API_KEY not set, skipping RouenOnEst")
            return []

        all_events: list[RawEvent] = []
        now = datetime.now(UTC)
        time_min = now.isoformat()
        time_max = (now + timedelta(days=30)).isoformat()

        for calendar_id, category_label in CALENDARS.items():
            events = await self._fetch_calendar(
                calendar_id, category_label, time_min=time_min, time_max=time_max
            )
            all_events.extend(events)

        logger.info(
            "RouenOnEst: fetched %d events from %d calendars", len(all_events), len(CALENDARS)
        )
        return all_events

    async def _fetch_calendar(
        self,
        calendar_id: str,
        category_label: str,
        time_min: str,
        time_max: str,
    ) -> list[RawEvent]:
        """Fetch upcoming events (within time window) from a single Google Calendar."""
        events: list[RawEvent] = []
        page_token: str | None = None

        while True:
            params: dict[str, str | int] = {
                "key": self._api_key,
                "timeMin": time_min,
                "timeMax": time_max,
                "singleEvents": "true",
                "orderBy": "startTime",
                "maxResults": 250,
            }
            if page_token:
                params["pageToken"] = page_token

            url = _GCAL_API.format(calendar_id=calendar_id)
            resp = await self._client.get(url, params=params)

            if resp.status_code == 403:
                logger.warning("Access denied for calendar %s — check API key", calendar_id[:20])
                break
            if resp.status_code == 404:
                logger.warning("Calendar not found: %s", calendar_id[:20])
                break
            resp.raise_for_status()

            try:
                data = resp.json()
            except Exception:
                logger.error("RouenOnEst [%s]: invalid JSON response", category_label)
                break

            for item in data.get("items", []):
                event = _parse_gcal_event(item, category_label)
                if event is not None:
                    events.append(event)

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        logger.info("RouenOnEst [%s]: %d events", category_label, len(events))
        return events


def _extract_time_from_title(title: str) -> tuple[str, str]:
    """Extract time from a title like 'Rouen Basket - Quimper (20h)' or 'Event (20h30)'.

    Returns (clean_title, time_str) where time_str is 'HH:MM', or (title, '') if not found.
    """
    m = _TIME_IN_TITLE_RE.search(title)
    if m:
        hours = int(m.group(1))
        minutes = m.group(2) or "00"
        time_str = f"{hours:02d}:{minutes}"
        return title[: m.start()].strip(), time_str
    return title, ""


def _parse_gcal_event(item: dict, category_label: str) -> RawEvent | None:
    """Parse a Google Calendar event into a RawEvent."""
    title = item.get("summary", "").strip()
    if not title:
        return None

    # Dates — can be date-only (all-day) or dateTime
    start = item.get("start", {})
    end = item.get("end", {})

    date_start = _extract_date(start)
    if date_start is None:
        return None
    date_end = _extract_date(end)

    # Time (only for non-all-day events)
    time_str = ""
    if "dateTime" in start:
        dt_str = start["dateTime"]
        if "T" in dt_str:
            time_str = dt_str.split("T")[1][:5]

    # Sports events are published as all-day events in Google Calendar, but carry
    # the actual time in the title as "(HHh)" or "(HHhMM)". Extract it and fix date_end.
    if category_label == _SPORTS_CATEGORY and "date" in start:
        title, time_str = _extract_time_from_title(title)
        # Google Calendar sets end to J+1 for all-day events; use date_start instead.
        date_end = date_start

    # Description and location
    description = item.get("description", "").strip()
    location = item.get("location", "").strip()

    # URL
    event_url = item.get("htmlLink", "")

    return RawEvent(
        title=title,
        description=description,
        date_start=date_start,
        date_end=date_end,
        time=time_str,
        location=location,
        url=event_url,
        source="rouen_on_est",
        raw_category=category_label,
    )


def _extract_date(dt_obj: dict) -> date | None:
    """Extract a date from a Google Calendar start/end object."""
    # All-day events use "date", timed events use "dateTime"
    if "date" in dt_obj:
        try:
            return date.fromisoformat(dt_obj["date"])
        except ValueError:
            return None
    if "dateTime" in dt_obj:
        try:
            return date.fromisoformat(dt_obj["dateTime"][:10])
        except ValueError:
            return None
    return None
