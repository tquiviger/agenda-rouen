"""Tests for the RouenOnEst Google Calendar scraper."""

from datetime import date
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from agenda_rouen.scrapers.rouen_on_est import (
    RouenOnEstScraper,
    _extract_date,
    _parse_gcal_event,
)

SAMPLE_GCAL_EVENT_TIMED = {
    "summary": "Concert de Jazz",
    "description": "Un super concert de jazz à Rouen.",
    "start": {"dateTime": "2026-03-20T20:30:00+01:00"},
    "end": {"dateTime": "2026-03-20T23:00:00+01:00"},
    "location": "Le 106, Rouen",
    "htmlLink": "https://www.google.com/calendar/event?eid=abc123",
}

SAMPLE_GCAL_EVENT_ALLDAY = {
    "summary": "Marché de Noël",
    "description": "",
    "start": {"date": "2026-12-01"},
    "end": {"date": "2026-12-24"},
    "location": "Place du Vieux-Marché, Rouen",
    "htmlLink": "https://www.google.com/calendar/event?eid=def456",
}

SAMPLE_GCAL_RESPONSE = {
    "items": [SAMPLE_GCAL_EVENT_TIMED, SAMPLE_GCAL_EVENT_ALLDAY],
}


class TestExtractDate:
    def test_date_only(self) -> None:
        assert _extract_date({"date": "2026-03-20"}) == date(2026, 3, 20)

    def test_datetime(self) -> None:
        assert _extract_date({"dateTime": "2026-03-20T20:30:00+01:00"}) == date(2026, 3, 20)

    def test_empty(self) -> None:
        assert _extract_date({}) is None

    def test_invalid(self) -> None:
        assert _extract_date({"date": "invalid"}) is None


class TestParseGcalEvent:
    def test_timed_event(self) -> None:
        event = _parse_gcal_event(SAMPLE_GCAL_EVENT_TIMED, "Culture & Expos")
        assert event is not None
        assert event.title == "Concert de Jazz"
        assert event.date_start == date(2026, 3, 20)
        assert event.time == "20:30"
        assert event.location == "Le 106, Rouen"
        assert event.raw_category == "Culture & Expos"
        assert event.source == "rouen_on_est"

    def test_allday_event(self) -> None:
        event = _parse_gcal_event(SAMPLE_GCAL_EVENT_ALLDAY, "Culture & Expos")
        assert event is not None
        assert event.title == "Marché de Noël"
        assert event.date_start == date(2026, 12, 1)
        assert event.date_end == date(2026, 12, 24)
        assert event.time == ""

    def test_no_title(self) -> None:
        assert _parse_gcal_event({"summary": "", "start": {"date": "2026-01-01"}}, "x") is None

    def test_no_start(self) -> None:
        assert _parse_gcal_event({"summary": "Test", "start": {}}, "x") is None


class TestRouenOnEstScraper:
    @pytest.mark.asyncio
    async def test_scrape_fetches_all_calendars(self) -> None:
        """Test that all 5 calendars are queried and events are collected."""
        request_urls: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            request_urls.append(str(request.url))
            return httpx.Response(200, json=SAMPLE_GCAL_RESPONSE)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with patch.dict("os.environ", {"GOOGLE_CALENDAR_API_KEY": "test-key"}):
            scraper = RouenOnEstScraper(client=client)
            async with scraper:
                events = await scraper.scrape()

        # 5 calendars × 2 events each
        assert len(events) == 10
        # All 5 calendars were queried
        assert len(request_urls) == 5

    @pytest.mark.asyncio
    async def test_scrape_sends_time_window_params(self) -> None:
        """Verify that timeMin and timeMax are sent in the request."""
        captured_params: dict[str, list[str]] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            parsed = urlparse(str(request.url))
            captured_params.update(parse_qs(parsed.query))
            return httpx.Response(200, json=SAMPLE_GCAL_RESPONSE)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with patch.dict("os.environ", {"GOOGLE_CALENDAR_API_KEY": "test-key"}):
            scraper = RouenOnEstScraper(client=client)
            async with scraper:
                await scraper.scrape()

        assert "timeMin" in captured_params
        assert "timeMax" in captured_params

    @pytest.mark.asyncio
    async def test_scrape_no_api_key(self) -> None:
        """Without API key, scraper returns empty list."""
        with patch.dict("os.environ", {}, clear=True):
            scraper = RouenOnEstScraper()
            async with scraper:
                events = await scraper.scrape()

        assert events == []
