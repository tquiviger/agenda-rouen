"""Integration tests for the Lambda handler."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agenda_rouen.handler import _build_scrapers, _run_pipeline, lambda_handler
from agenda_rouen.models import RawEvent


def _make_raw(title: str = "Event", source: str = "test") -> RawEvent:
    return RawEvent(
        title=title,
        date_start=date(2026, 3, 20),
        url=f"https://example.com/{title}",
        source=source,
        raw_category="Concerts à Rouen",
        description="",
        location="",
    )


class TestBuildScrapers:
    def test_returns_all_active_scrapers(self) -> None:
        scrapers = _build_scrapers()
        names = [s.name for s in scrapers]
        # JDS + RouenOnEst + 3 OpenAgenda
        assert len(scrapers) == 5
        assert "jds" in names
        assert "rouen_on_est" in names
        assert "openagenda_metropole" in names
        assert "openagenda_rouen" in names
        assert "openagenda_bibliotheques" in names


class TestRunPipeline:
    @pytest.mark.asyncio
    async def test_scrape_classify_publish(self) -> None:
        """Full pipeline: scrape → classify → publish."""
        raw = [_make_raw("Concert A"), _make_raw("Concert B")]

        with (
            patch("agenda_rouen.handler._build_scrapers") as mock_build,
            patch("agenda_rouen.handler.classify") as mock_classify,
            patch("agenda_rouen.handler.publish_to_s3") as mock_publish,
            patch("agenda_rouen.handler.CLOUDFRONT_DISTRIBUTION_ID", ""),
        ):
            # Mock a single scraper returning 2 events
            mock_scraper = MagicMock()
            mock_scraper.name = "mock"
            mock_scraper.__aenter__ = AsyncMock(return_value=mock_scraper)
            mock_scraper.__aexit__ = AsyncMock(return_value=None)
            mock_scraper.scrape = AsyncMock(return_value=raw)
            mock_build.return_value = [mock_scraper]

            mock_classify.return_value = [MagicMock(), MagicMock()]
            mock_publish.return_value = ["events.json", "dates/2026-03-20.json"]

            result = await _run_pipeline()

        assert result["raw_count"] == 2
        assert result["classified_count"] == 2
        assert result["files_published"] == 2
        mock_classify.assert_called_once()
        mock_publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_scraper_failure_does_not_crash_pipeline(self) -> None:
        """If one scraper fails, the pipeline continues with the others."""
        with (
            patch("agenda_rouen.handler._build_scrapers") as mock_build,
            patch("agenda_rouen.handler.classify") as mock_classify,
            patch("agenda_rouen.handler.publish_to_s3") as mock_publish,
            patch("agenda_rouen.handler.CLOUDFRONT_DISTRIBUTION_ID", ""),
        ):
            # Failing scraper
            failing = MagicMock()
            failing.name = "failing"
            failing.__aenter__ = AsyncMock(return_value=failing)
            failing.__aexit__ = AsyncMock(return_value=None)
            failing.scrape = AsyncMock(side_effect=Exception("boom"))

            # Working scraper
            working = MagicMock()
            working.name = "working"
            working.__aenter__ = AsyncMock(return_value=working)
            working.__aexit__ = AsyncMock(return_value=None)
            working.scrape = AsyncMock(return_value=[_make_raw()])

            mock_build.return_value = [failing, working]
            mock_classify.return_value = [MagicMock()]
            mock_publish.return_value = ["events.json"]

            result = await _run_pipeline()

        # Pipeline succeeded despite one scraper failing
        assert result["raw_count"] == 1
        assert result["classified_count"] == 1


class TestLambdaHandler:
    def test_returns_200_with_body(self) -> None:
        with (
            patch("agenda_rouen.handler._build_scrapers") as mock_build,
            patch("agenda_rouen.handler.classify") as mock_classify,
            patch("agenda_rouen.handler.publish_to_s3") as mock_publish,
            patch("agenda_rouen.handler.CLOUDFRONT_DISTRIBUTION_ID", ""),
        ):
            mock_build.return_value = []
            mock_classify.return_value = []
            mock_publish.return_value = []

            response = lambda_handler({}, None)

        assert response["statusCode"] == 200
        assert "body" in response
        assert response["body"]["raw_count"] == 0
