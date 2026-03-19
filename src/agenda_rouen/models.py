"""Event data models."""

from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Category(StrEnum):
    """Unified event taxonomy."""

    MUSIC = "musique"
    PERFORMING_ARTS = "spectacles"  # théâtre, danse, cirque
    SPORT = "sport"
    EXHIBITION = "expositions"
    CINEMA = "cinéma"
    FESTIVAL = "festival"
    CONFERENCE = "conférences"
    WORKSHOP = "ateliers"
    FAMILY = "famille"
    FOOD = "gastronomie"
    NIGHTLIFE = "vie-nocturne"
    OTHER = "autre"


class RawEvent(BaseModel):
    """Event as scraped from a source, before classification."""

    title: str
    description: str = ""
    date_start: date
    date_end: date | None = None
    time: str = ""  # free-form time string, e.g. "20h30"
    location: str = ""
    address: str = ""
    url: str
    image_url: str = ""
    source: str  # identifier of the scraper that produced this event
    raw_category: str = ""  # category as labeled by the source site


class Event(BaseModel):
    """Classified and deduplicated event, ready for publication."""

    id: str = Field(description="Deterministic hash from title + date + location")
    title: str
    description: str = ""
    date_start: date
    date_end: date | None = None
    time: str = ""
    location: str = ""
    address: str = ""
    category: Category
    tags: list[str] = Field(default_factory=list)
    urls: list[str] = Field(description="Source URLs (may come from multiple sources)")
    image_url: str = ""
    sources: list[str] = Field(description="Scraper identifiers that found this event")
    classified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
