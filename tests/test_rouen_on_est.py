"""Tests for the RouenOnEst Google Calendar scraper."""

from datetime import date
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from agenda_rouen.scrapers.rouen_on_est import (
    RouenOnEstScraper,
    _extract_date,
    _extract_time_from_title,
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

# Sports event: all-day in Google Calendar, time embedded in title
SAMPLE_GCAL_EVENT_SPORTS = {
    "summary": "Rouen Basket - Quimper (20h)",
    "description": "",
    "start": {"date": "2026-03-22"},
    "end": {"date": "2026-03-23"},  # Google Calendar J+1 convention
    "location": "Kindarena, Rouen",
    "htmlLink": "https://www.google.com/calendar/event?eid=sports123",
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


class TestExtractTimeFromTitle:
    def test_hour_only(self) -> None:
        assert _extract_time_from_title("Rouen Basket - Quimper (20h)") == (
            "Rouen Basket - Quimper",
            "20:00",
        )

    def test_hour_and_minutes(self) -> None:
        assert _extract_time_from_title("Concert (20h30)") == ("Concert", "20:30")

    def test_single_digit_hour(self) -> None:
        assert _extract_time_from_title("Event (9h)") == ("Event", "09:00")

    def test_no_time(self) -> None:
        assert _extract_time_from_title("Marché de Noël") == ("Marché de Noël", "")

    def test_no_time_with_parentheses(self) -> None:
        # Parentheses not matching the time pattern should be left alone
        assert _extract_time_from_title("Event (special)") == ("Event (special)", "")

    def test_strips_surrounding_whitespace(self) -> None:
        title, time_str = _extract_time_from_title("  Event  (14h00)  ")
        assert title == "Event"
        assert time_str == "14:00"


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

    def test_sports_allday_extracts_time_and_fixes_date(self) -> None:
        event = _parse_gcal_event(SAMPLE_GCAL_EVENT_SPORTS, "Sports & Compétitions")
        assert event is not None
        # Time extracted from title
        assert event.title == "Rouen Basket - Quimper"
        assert event.time == "20:00"
        # date_end corrected to date_start (not J+1)
        assert event.date_start == date(2026, 3, 22)
        assert event.date_end == date(2026, 3, 22)

    def test_sports_allday_no_time_in_title(self) -> None:
        item = {
            "summary": "Rouen Handball - Paris (déplacement)",
            "start": {"date": "2026-03-22"},
            "end": {"date": "2026-03-23"},
            "htmlLink": "",
        }
        event = _parse_gcal_event(item, "Sports & Compétitions")
        assert event is not None
        assert event.title == "Rouen Handball - Paris (déplacement)"
        assert event.time == ""
        assert event.date_end == date(2026, 3, 22)

    def test_non_sports_allday_keeps_date_end(self) -> None:
        # Non-sports all-day events must NOT have their date_end altered
        event = _parse_gcal_event(SAMPLE_GCAL_EVENT_ALLDAY, "Culture & Expos")
        assert event is not None
        assert event.date_start == date(2026, 12, 1)
        assert event.date_end == date(2026, 12, 24)

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
