"""Tests for event models."""

from datetime import date

from agenda_rouen.models import Category, Event, RawEvent


def test_raw_event_minimal() -> None:
    event = RawEvent(
        title="Concert Test",
        date_start=date(2026, 3, 20),
        url="https://example.com/event",
        source="test",
    )
    assert event.title == "Concert Test"
    assert event.description == ""
    assert event.date_end is None


def test_event_category_enum() -> None:
    event = Event(
        id="abc123",
        title="Match de foot",
        date_start=date(2026, 3, 20),
        category=Category.SPORT,
        urls=["https://example.com"],
        sources=["test"],
    )
    assert event.category == Category.SPORT
    assert event.category.value == "sport"


def test_event_from_string_category() -> None:
    event = Event(
        id="abc123",
        title="Théâtre",
        date_start=date(2026, 3, 20),
        category="spectacles",
        urls=["https://example.com"],
        sources=["test"],
    )
    assert event.category == Category.PERFORMING_ARTS
