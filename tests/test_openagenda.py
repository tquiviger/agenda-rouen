"""Tests for the OpenAgenda scraper."""

from datetime import date
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from agenda_rouen.scrapers.openagenda import OpenAgendaScraper, _get_fr, _parse_date, _parse_event

# Minimal event payload matching OpenAgenda v2 JSON structure
SAMPLE_EVENT = {
    "uid": 55675681,
    "slug": "albumine-collodion-rouen-en-photographies-1850-1920",
    "title": {"fr": "Albumine & Collodion — Rouen en photographies"},
    "description": {"fr": "Exposition de photographies historiques de Rouen."},
    "firstTiming": {
        "begin": "2026-03-07T10:00:00+01:00",
        "end": "2026-03-07T18:00:00+01:00",
    },
    "lastTiming": {
        "begin": "2026-07-31T10:00:00+02:00",
        "end": "2026-07-31T18:00:00+02:00",
    },
    "location": {
        "name": "Archives départementales",
        "address": "42 rue Henri II Plantagenêt",
        "postalCode": "76100",
        "city": "Rouen",
    },
    "image": {"base": "https://cdn.openagenda.com/main/abc123.jpg"},
    "registration": [
        {"type": "link", "value": "https://bibliotheques.rouen.fr/agenda/albumine-collodion"},
    ],
    "links": [],
}

SAMPLE_API_RESPONSE = {
    "total": 2,
    "events": [
        SAMPLE_EVENT,
        {
            "uid": 99999,
            "slug": "concert-rock",
            "title": {"fr": "Concert Rock"},
            "description": {"fr": "Un concert de rock."},
            "firstTiming": {
                "begin": "2026-04-01T20:30:00+02:00",
                "end": "2026-04-01T23:00:00+02:00",
            },
            "lastTiming": {
                "begin": "2026-04-01T20:30:00+02:00",
                "end": "2026-04-01T23:00:00+02:00",
            },
            "location": {"name": "Le 106", "address": "", "postalCode": "", "city": "Rouen"},
            "image": {},
        },
    ],
    "sort": None,
}


class TestHelpers:
    def test_get_fr_dict(self) -> None:
        assert _get_fr({"fr": "Bonjour", "en": "Hello"}) == "Bonjour"

    def test_get_fr_string(self) -> None:
        assert _get_fr("Direct string") == "Direct string"

    def test_get_fr_none(self) -> None:
        assert _get_fr(None) == ""

    def test_parse_date_valid(self) -> None:
        assert _parse_date("2026-03-07T10:00:00+01:00") == date(2026, 3, 7)

    def test_parse_date_none(self) -> None:
        assert _parse_date(None) is None

    def test_parse_date_invalid(self) -> None:
        assert _parse_date("not-a-date") is None


class TestParseEvent:
    def test_parse_full_event(self) -> None:
        event = _parse_event(SAMPLE_EVENT, source="test")
        assert event is not None
        assert event.title == "Albumine & Collodion — Rouen en photographies"
        assert event.date_start == date(2026, 3, 7)
        assert event.date_end == date(2026, 7, 31)
        assert event.time == "10:00"
        assert event.location == "Archives départementales"
        assert "76100" in event.address
        assert "Rouen" in event.address
        assert event.source == "test"
        assert "cdn.openagenda.com" in event.image_url

    def test_url_from_registration(self) -> None:
        """URL comes from registration[].value when type is 'link'."""
        event = _parse_event(SAMPLE_EVENT, source="test")
        assert event is not None
        assert event.url == "https://bibliotheques.rouen.fr/agenda/albumine-collodion"

    def test_url_from_links_fallback(self) -> None:
        """Falls back to links[].link when registration is empty."""
        raw = {
            **SAMPLE_EVENT,
            "registration": [],
            "links": [{"link": "https://www.metropole-rouen-normandie.fr/event/42"}],
        }
        event = _parse_event(raw, source="test")
        assert event is not None
        assert event.url == "https://www.metropole-rouen-normandie.fr/event/42"

    def test_url_empty_when_no_registration_no_links(self) -> None:
        """URL is empty when neither registration nor links are present."""
        raw = {**SAMPLE_EVENT, "registration": [], "links": []}
        event = _parse_event(raw, source="test")
        assert event is not None
        assert event.url == ""

    def test_url_ignores_non_link_registration_types(self) -> None:
        """registration entries with type != 'link' (e.g. 'email') are ignored."""
        raw = {
            **SAMPLE_EVENT,
            "registration": [{"type": "email", "value": "contact@example.com"}],
            "links": [{"link": "https://fallback.example.com"}],
        }
        event = _parse_event(raw, source="test")
        assert event is not None
        assert event.url == "https://fallback.example.com"

    def test_parse_event_no_title(self) -> None:
        raw = {**SAMPLE_EVENT, "title": {"fr": ""}}
        assert _parse_event(raw, source="test") is None

    def test_parse_event_no_timing(self) -> None:
        raw = {**SAMPLE_EVENT, "firstTiming": {}}
        assert _parse_event(raw, source="test") is None


class TestOpenAgendaScraper:
    @pytest.mark.asyncio
    async def test_scrape_single_page(self) -> None:
        """Test scraping with a mocked HTTP response (single page, < PAGE_SIZE)."""
        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json=SAMPLE_API_RESPONSE)
        )
        client = httpx.AsyncClient(transport=transport)

        scraper = OpenAgendaScraper(
            agenda_name="test_agenda",
            agenda_uid=12345,
            client=client,
        )
        async with scraper:
            events = await scraper.scrape()

        assert len(events) == 2
        assert events[0].title == "Albumine & Collodion — Rouen en photographies"
        assert events[1].title == "Concert Rock"
        assert events[0].source == "test_agenda"

    @pytest.mark.asyncio
    async def test_scrape_sends_time_window_params(self) -> None:
        """Verify that timings[gte] and timings[lte] are sent in the request."""
        captured_params: dict[str, list[str]] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            parsed = urlparse(str(request.url))
            captured_params.update(parse_qs(parsed.query))
            return httpx.Response(200, json=SAMPLE_API_RESPONSE)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        scraper = OpenAgendaScraper(
            agenda_name="test_agenda",
            agenda_uid=12345,
            client=client,
        )
        async with scraper:
            await scraper.scrape()

        assert "timings[gte]" in captured_params
        assert "timings[lte]" in captured_params
