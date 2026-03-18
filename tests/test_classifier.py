"""Tests for the LLM classifier (batching and dedup logic)."""

from datetime import UTC, date, datetime

from agenda_rouen.classifier.llm import _event_id, _merge_duplicates
from agenda_rouen.models import Category, Event


def _make_event(
    title: str = "Concert",
    date_start: date = date(2026, 3, 20),
    location: str = "Le 106",
    **kwargs: object,
) -> Event:
    eid = _event_id(title, str(date_start), location)
    defaults = {
        "id": eid,
        "title": title,
        "description": "",
        "date_start": date_start,
        "category": Category.MUSIC,
        "urls": [f"https://example.com/{eid}"],
        "sources": ["source_a"],
        "tags": ["rock"],
        "image_url": "",
        "classified_at": datetime(2026, 3, 18, 12, 0, tzinfo=UTC),
        "location": location,
    }
    defaults.update(kwargs)
    return Event(**defaults)


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


class TestMergeDuplicates:
    def test_no_duplicates(self) -> None:
        events = [
            _make_event(title="Concert A"),
            _make_event(title="Concert B"),
        ]
        merged = _merge_duplicates(events)
        assert len(merged) == 2

    def test_merge_urls_and_sources(self) -> None:
        event1 = _make_event(
            urls=["https://a.com/1"],
            sources=["source_a"],
        )
        event2 = _make_event(
            urls=["https://b.com/2"],
            sources=["source_b"],
        )
        merged = _merge_duplicates([event1, event2])
        assert len(merged) == 1
        assert "https://a.com/1" in merged[0].urls
        assert "https://b.com/2" in merged[0].urls
        assert "source_a" in merged[0].sources
        assert "source_b" in merged[0].sources

    def test_merge_keeps_longest_description(self) -> None:
        event1 = _make_event(description="Short")
        event2 = _make_event(description="A much longer description with details")
        merged = _merge_duplicates([event1, event2])
        assert merged[0].description == "A much longer description with details"

    def test_merge_tags(self) -> None:
        event1 = _make_event(tags=["rock", "live"])
        event2 = _make_event(tags=["rock", "concert"])
        merged = _merge_duplicates([event1, event2])
        assert set(merged[0].tags) == {"rock", "live", "concert"}

    def test_merge_keeps_image(self) -> None:
        event1 = _make_event(image_url="https://img.com/pic.jpg")
        event2 = _make_event(image_url="")
        merged = _merge_duplicates([event1, event2])
        assert merged[0].image_url == "https://img.com/pic.jpg"

    def test_merge_fills_missing_image(self) -> None:
        event1 = _make_event(image_url="")
        event2 = _make_event(image_url="https://img.com/pic.jpg")
        merged = _merge_duplicates([event1, event2])
        assert merged[0].image_url == "https://img.com/pic.jpg"

    def test_no_duplicate_urls(self) -> None:
        event1 = _make_event(urls=["https://same.com"])
        event2 = _make_event(urls=["https://same.com"])
        merged = _merge_duplicates([event1, event2])
        assert merged[0].urls == ["https://same.com"]
