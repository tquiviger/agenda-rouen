"""Tests for the LLM classifier."""

from agenda_rouen.classifier.llm import _event_id


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
