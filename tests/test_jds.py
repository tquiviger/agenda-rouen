"""Tests for the JDS scraper."""

from datetime import date, timedelta
from unittest.mock import patch

import httpx
import pytest

from agenda_rouen.scrapers.jds import (
    JdsScraper,
    _day_url,
    _parse_date_text,
    _parse_fr_date,
)

# Use a fixed "today" so tests are deterministic (Wednesday March 18, 2026)
FAKE_TODAY = date(2026, 3, 18)
WITHIN_WINDOW = FAKE_TODAY + timedelta(days=5)  # 2026-03-23


def _fmt(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def _make_html(*events_data: tuple[str, str, str, str]) -> str:
    """Build a minimal JDS HTML page from (title, date_text, location, url_id) tuples."""
    cards = []
    for title, date_text, location, url_id in events_data:
        cards.append(f"""\
  <li class="col-12 pt-3" data-view-id-type="1" data-view-id="{url_id}" data-view-bc="0">
    <div class="d-flex justify-content-between pb-4 border-bottom flex-row-reverse">
      <div class="pave d-flex flex-column justify-content-between d-md-block">
        <div class="m-0 mb-1 rubriques font-size-14 text-primary">
          <a href="#" class="lh-sm">Catégorie</a>
        </div>
        <a class="d-block titre text-black mb-1 mb-md-2"
           href="https://www.jds.fr/rouen/event/{url_id}_A">
          <span class="font-size-18 fw-bold lh-1 d-block titre text-black mb-2">
            {title}
          </span>
        </a>
        <span class="font-size-14 text-gray-700 lh-sm d-block">{date_text}</span>
        <span class="lieu font-size-14 text-gray-700 d-block lh-sm my-1">
          {location}
        </span>
      </div>
    </div>
  </li>""")
    inner = "\n".join(cards)
    return f"""\
<html><body>
<ul class="mt-3 list-unstyled list-articles-v2" id="liste-dates-abc">
{inner}
</ul>
</body></html>"""


EMPTY_HTML = "<html><body><ul class='list-articles-v2'></ul></body></html>"


class TestDayUrl:
    def test_known_wednesday(self) -> None:
        # March 18, 2026 is a Wednesday (weekday=2)
        url = _day_url(date(2026, 3, 18))
        assert url == (
            "https://www.jds.fr/rouen/agenda/agenda-du-jour"
            "/mercredi-18-mars-2026-18-3-2026_JPJ"
        )

    def test_saturday(self) -> None:
        # March 21, 2026 is a Saturday (weekday=5)
        url = _day_url(date(2026, 3, 21))
        assert "samedi-21-mars-2026-21-3-2026_JPJ" in url

    def test_month_no_leading_zero(self) -> None:
        # April → month number 4, no leading zero
        url = _day_url(date(2026, 4, 1))
        assert "1-avril-2026-1-4-2026_JPJ" in url

    def test_august_uses_aout(self) -> None:
        url = _day_url(date(2026, 8, 15))
        assert "août" in url


class TestDateParsing:
    def test_single_date(self) -> None:
        start, end = _parse_date_text("Le 24/03/2026")
        assert start == date(2026, 3, 24)
        assert end is None

    def test_date_range(self) -> None:
        start, end = _parse_date_text("Du 18/03/2026 au 04/11/2026")
        assert start == date(2026, 3, 18)
        assert end == date(2026, 11, 4)

    def test_no_date(self) -> None:
        start, end = _parse_date_text("Bientôt")
        assert start is None
        assert end is None

    def test_parse_fr_date(self) -> None:
        assert _parse_fr_date("24/03/2026") == date(2026, 3, 24)

    def test_parse_fr_date_invalid(self) -> None:
        assert _parse_fr_date("invalid") is None


class TestJdsScraper:
    @pytest.mark.asyncio
    async def test_scrape_fetches_30_day_urls(self) -> None:
        """Exactly 30 per-day URLs are requested."""
        request_urls: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            request_urls.append(str(request.url))
            return httpx.Response(200, text=EMPTY_HTML)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with patch("agenda_rouen.scrapers.jds.date") as mock_date:
            mock_date.today.return_value = FAKE_TODAY
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            scraper = JdsScraper(client=client)
            async with scraper:
                await scraper.scrape()

        assert len(request_urls) == 30
        assert all("agenda-du-jour" in url for url in request_urls)
        # First URL must be today
        assert "mercredi-18-mars-2026" in request_urls[0]

    @pytest.mark.asyncio
    async def test_scrape_parses_events(self) -> None:
        """Events on day pages are returned."""
        html = _make_html(
            ("Concert Rock", f"Le {_fmt(WITHIN_WINDOW)}", "Le 106", "1001"),
            ("Match Rugby", f"Le {_fmt(WITHIN_WINDOW)}", "Stade Diochon", "1002"),
        )
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(200, text=html)
            return httpx.Response(200, text=EMPTY_HTML)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with patch("agenda_rouen.scrapers.jds.date") as mock_date:
            mock_date.today.return_value = FAKE_TODAY
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            scraper = JdsScraper(client=client)
            async with scraper:
                events = await scraper.scrape()

        assert len(events) == 2
        assert events[0].title == "Concert Rock"
        assert events[0].source == "jds"
        assert events[1].title == "Match Rugby"

    @pytest.mark.asyncio
    async def test_scrape_deduplicates_multiday_events(self) -> None:
        """A multi-day event appearing on every day page is counted only once."""
        html_with_event = _make_html(
            ("Festival XYZ", f"Du {_fmt(FAKE_TODAY)} au {_fmt(WITHIN_WINDOW)}", "Parc", "event_42"),
        )

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text=html_with_event)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with patch("agenda_rouen.scrapers.jds.date") as mock_date:
            mock_date.today.return_value = FAKE_TODAY
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            scraper = JdsScraper(client=client)
            async with scraper:
                events = await scraper.scrape()

        assert len(events) == 1
        assert events[0].title == "Festival XYZ"

    @pytest.mark.asyncio
    async def test_scrape_skips_404_days(self) -> None:
        """404 responses are skipped and do not raise an error."""
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(404, text="Not Found")
            return httpx.Response(200, text=EMPTY_HTML)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with patch("agenda_rouen.scrapers.jds.date") as mock_date:
            mock_date.today.return_value = FAKE_TODAY
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            scraper = JdsScraper(client=client)
            async with scraper:
                events = await scraper.scrape()

        # All 30 URLs attempted, first returned 404 (skipped), rest returned empty
        assert call_count == 30
        assert events == []
