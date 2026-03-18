"""Scraper for jds.fr (Journal des Spectacles) — Rouen agenda."""

from __future__ import annotations

import logging
import re
from datetime import date, timedelta

from bs4 import BeautifulSoup, Tag

from agenda_rouen.models import RawEvent
from agenda_rouen.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.jds.fr/rouen/agenda/"
_MAX_PAGES = 10


class JdsScraper(BaseScraper):
    name = "jds"

    async def scrape(self) -> list[RawEvent]:
        events: list[RawEvent] = []
        today = date.today()
        cutoff = today + timedelta(days=30)

        for page in range(1, _MAX_PAGES + 1):
            url = f"{_BASE_URL}?&page={page}"
            resp = await self._client.get(url)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "lxml")
            cards = soup.select("ul.list-articles-v2 > li.col-12[data-view-id]")

            if not cards:
                break

            kept = 0
            for card in cards:
                event = _parse_card(card)
                if event is None:
                    continue
                if event.date_start > cutoff:
                    continue
                events.append(event)
                kept += 1

            logger.info("JDS page %d: %d/%d events in window", page, kept, len(cards))

            # Stop paginating when no events on the page fall within the window
            if kept == 0:
                break

        logger.info("JDS total: %d events", len(events))
        return events


def _parse_card(card: Tag) -> RawEvent | None:
    """Parse a single JDS event card."""
    # Title + URL
    title_link = card.select_one("a.d-block.titre")
    if not title_link:
        return None

    title_span = title_link.select_one("span")
    title = title_span.get_text(strip=True) if title_span else title_link.get_text(strip=True)
    event_url = title_link.get("href", "")

    if not title or not event_url:
        return None

    # Category
    cat_el = card.select_one("div.rubriques a")
    raw_category = cat_el.get_text(strip=True) if cat_el else ""

    # Date
    date_el = card.select_one("span.font-size-14.text-gray-700.lh-sm")
    date_text = date_el.get_text(strip=True) if date_el else ""
    date_start, date_end = _parse_date_text(date_text)

    if date_start is None:
        return None

    # Location (can be <a class="lieu"> or <span class="lieu">)
    loc_el = card.select_one(".lieu")
    location = loc_el.get_text(strip=True) if loc_el else ""

    # Image
    img_el = card.select_one("div.pave-image img")
    image_url = img_el.get("src", "") if img_el else ""

    # Description
    desc_el = card.select_one("span.description")
    description = desc_el.get_text(strip=True) if desc_el else ""

    return RawEvent(
        title=title,
        description=description,
        date_start=date_start,
        date_end=date_end,
        location=location,
        url=str(event_url),
        image_url=str(image_url),
        source="jds",
        raw_category=raw_category,
    )


def _parse_date_text(text: str) -> tuple[date | None, date | None]:
    """Parse JDS date strings like 'Le 24/03/2026' or 'Du 18/03/2026 au 04/11/2026'."""
    # Single date: "Le DD/MM/YYYY"
    single = re.search(r"Le\s+(\d{2}/\d{2}/\d{4})", text)
    if single:
        d = _parse_fr_date(single.group(1))
        return d, None

    # Date range: "Du DD/MM/YYYY au DD/MM/YYYY"
    range_match = re.search(
        r"Du\s+(\d{2}/\d{2}/\d{4})\s+au\s+(\d{2}/\d{2}/\d{4})", text
    )
    if range_match:
        start = _parse_fr_date(range_match.group(1))
        end = _parse_fr_date(range_match.group(2))
        return start, end

    return None, None


def _parse_fr_date(text: str) -> date | None:
    """Parse DD/MM/YYYY into a date."""
    try:
        parts = text.split("/")
        return date(int(parts[2]), int(parts[1]), int(parts[0]))
    except (ValueError, IndexError):
        return None
