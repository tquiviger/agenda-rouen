"""Tests for the LLM classifier."""

from datetime import date

import pytest

from agenda_rouen.classifier.llm import _event_id, classify
from agenda_rouen.models import RawEvent


def _make_raw(
    title: str = "Concert Rock",
    date_start: date = date(2026, 3, 20),
    **kwargs: object,
) -> RawEvent:
    defaults = {
        "title": title,
        "date_start": date_start,
        "url": f"https://example.com/{title.lower().replace(' ', '-')}",
        "source": "test",
        "raw_category": "Concerts à Rouen",
        "description": "",
        "location": "",
    }
    defaults.update(kwargs)
    return RawEvent(**defaults)


class TestEventId:
    def test_deterministic(self) -> None:
        id1 = _event_id("Concert Rock", "2026-03-20", "Le 106")
        id2 = _event_id("Concert Rock", "2026-03-20", "Le 106")
        assert id1 == id2

    def test_case_insensitive(self) -> None:
        id1 = _event_id("Concert Rock", "2026-03-20", "Le 106")
        id2 = _event_id("concert rock", "2026-03-20", "le 106")
        assert id1 == id2

    def test_different_events(self) -> None:
        id1 = _event_id("Concert Rock", "2026-03-20", "Le 106")
        id2 = _event_id("Concert Jazz", "2026-03-20", "Le 106")
        assert id1 != id2


class TestDedup:
    @pytest.mark.asyncio
    async def test_same_title_same_date_deduped(self) -> None:
        raw = [
            _make_raw(title="Concert Rock", date_start=date(2026, 3, 20), source="a"),
            _make_raw(title="Concert Rock", date_start=date(2026, 3, 20), source="b"),
        ]
        events = await classify(raw)
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_case_insensitive_dedup(self) -> None:
        raw = [
            _make_raw(title="Concert Rock", date_start=date(2026, 3, 20)),
            _make_raw(title="concert rock", date_start=date(2026, 3, 20)),
        ]
        events = await classify(raw)
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_same_title_different_date_kept(self) -> None:
        raw = [
            _make_raw(title="Concert Rock", date_start=date(2026, 3, 20)),
            _make_raw(title="Concert Rock", date_start=date(2026, 3, 21)),
        ]
        events = await classify(raw)
        assert len(events) == 2

    @pytest.mark.asyncio
    async def test_different_title_same_date_kept(self) -> None:
        raw = [
            _make_raw(title="Concert Rock", date_start=date(2026, 3, 20)),
            _make_raw(title="Concert Jazz", date_start=date(2026, 3, 20)),
        ]
        events = await classify(raw)
        assert len(events) == 2

    @pytest.mark.asyncio
    async def test_keeps_longest_description(self) -> None:
        raw = [
            _make_raw(title="Concert Rock", description="Short"),
            _make_raw(title="Concert Rock", description="A much longer description"),
        ]
        events = await classify(raw)
        assert len(events) == 1
        assert events[0].description == "A much longer description"


class TestSourceOverrides:
    @pytest.mark.asyncio
    async def test_bibliotheques_source_forced_to_workshop(self) -> None:
        """Events from openagenda_bibliotheques are always categorized as ateliers."""
        raw = [_make_raw(source="openagenda_bibliotheques", raw_category="Culture & Expos")]
        events = await classify(raw)
        assert len(events) == 1
        assert events[0].category == "ateliers"

    @pytest.mark.asyncio
    async def test_bibliotheques_no_raw_category_still_workshop(self) -> None:
        """Even without raw_category, bibliotheques events are forced to ateliers."""
        raw = [_make_raw(source="openagenda_bibliotheques", raw_category="")]
        events = await classify(raw)
        assert len(events) == 1
        assert events[0].category == "ateliers"

    @pytest.mark.asyncio
    async def test_other_source_not_overridden(self) -> None:
        """Source override only applies to openagenda_bibliotheques."""
        raw = [_make_raw(source="openagenda_metropole", raw_category="Concerts à Rouen")]
        events = await classify(raw)
        assert len(events) == 1
        assert events[0].category == "musique"

    @pytest.mark.asyncio
    async def test_bibliotheques_wins_dedup_over_metropole(self) -> None:
        """When the same event appears in both metropole and bibliotheques,
        the bibliotheques version wins dedup and the ateliers override applies."""
        raw = [
            # metropole version — longer description, would normally win
            _make_raw(
                title="Atelier poterie",
                source="openagenda_metropole",
                raw_category="Ateliers à Rouen",
                description="Une très longue description pour cet atelier de poterie.",
            ),
            # bibliotheques version — shorter description but source override
            _make_raw(
                title="Atelier poterie",
                source="openagenda_bibliotheques",
                raw_category="Ateliers à Rouen",
                description="Court.",
            ),
        ]
        events = await classify(raw)
        assert len(events) == 1
        assert events[0].category == "ateliers"


class TestExcludedCategories:
    @pytest.mark.asyncio
    async def test_conferences_excluded(self) -> None:
        raw = [_make_raw(raw_category="Conférences à Rouen")]
        events = await classify(raw)
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_gastronomie_excluded(self) -> None:
        raw = [_make_raw(raw_category="Gastronomie à Rouen")]
        events = await classify(raw)
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_marches_excluded(self) -> None:
        raw = [_make_raw(raw_category="Marchés à Rouen")]
        events = await classify(raw)
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_non_excluded_kept(self) -> None:
        raw = [
            _make_raw(title="Concert", raw_category="Concerts à Rouen"),
            _make_raw(title="Conférence", raw_category="Conférences à Rouen"),
            _make_raw(title="Marché", raw_category="Marchés à Rouen"),
        ]
        events = await classify(raw)
        assert len(events) == 1
        assert events[0].title == "Concert"
