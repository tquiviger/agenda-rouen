"""Use Google Gemini to classify events into categories and deduplicate."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import UTC, datetime

from google import genai

from agenda_rouen.models import Category, Event, RawEvent

logger = logging.getLogger(__name__)

_BATCH_SIZE = 30

_SYSTEM_PROMPT = """\
Tu es un assistant spécialisé dans la classification d'événements culturels et sportifs \
à Rouen et ses environs.

Catégories disponibles : {categories}

Tu reçois une liste d'événements bruts (JSON). Pour chaque événement, tu dois :
1. Assigner la catégorie la plus pertinente parmi la liste ci-dessus.
2. Générer 1 à 3 tags descriptifs (en français, minuscules).
3. Identifier les doublons : si deux événements ont le même titre (ou très similaire), \
   la même date et le même lieu, regroupe-les en un seul avec les URLs combinées.

Réponds en JSON strict (pas de markdown) avec la structure :
[
  {{
    "title": "...",
    "description": "...",
    "date_start": "YYYY-MM-DD",
    "date_end": "YYYY-MM-DD or null",
    "time": "...",
    "location": "...",
    "address": "...",
    "category": "...",
    "tags": ["..."],
    "urls": ["..."],
    "image_url": "...",
    "sources": ["..."]
  }}
]
"""


def _event_id(title: str, date_start: str, location: str) -> str:
    """Generate a deterministic ID from key event fields."""
    raw = f"{title.lower().strip()}|{date_start}|{location.lower().strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _get_client() -> genai.Client:
    """Create a Gemini client (singleton-friendly, reused across batches)."""
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


async def classify_and_dedup(
    raw_events: list[RawEvent],
    *,
    model: str = "gemini-2.5-flash",
    batch_size: int = _BATCH_SIZE,
) -> list[Event]:
    """Classify and deduplicate events via Gemini.

    Splits events into batches, classifies each batch, then merges
    duplicates across batches using a deterministic ID.
    """
    if not raw_events:
        return []

    client = _get_client()

    # Split into batches
    batches = [
        raw_events[i : i + batch_size]
        for i in range(0, len(raw_events), batch_size)
    ]
    logger.info(
        "Classifying %d events in %d batches of %d",
        len(raw_events), len(batches), batch_size,
    )

    # Classify each batch sequentially (sync API — more reliable in Lambda)
    all_classified: list[Event] = []
    for i, batch in enumerate(batches):
        logger.info("Classifying batch %d/%d (%d events)", i + 1, len(batches), len(batch))
        try:
            events = _classify_batch(client, batch, model=model)
            all_classified.extend(events)
        except Exception:
            logger.exception("Failed to classify batch %d/%d, skipping", i + 1, len(batches))

    # Merge duplicates across batches
    merged = _merge_duplicates(all_classified)
    logger.info(
        "Classification done: %d → %d events (after cross-batch dedup)",
        len(all_classified), len(merged),
    )
    return merged


def _classify_batch(
    client: genai.Client,
    raw_events: list[RawEvent],
    *,
    model: str,
) -> list[Event]:
    """Send a single batch to Gemini for classification (sync API)."""
    categories = ", ".join(c.value for c in Category)
    system = _SYSTEM_PROMPT.format(categories=categories)

    events_json = json.dumps(
        [e.model_dump(mode="json") for e in raw_events],
        ensure_ascii=False,
    )

    response = client.models.generate_content(
        model=model,
        contents=events_json,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=16384,
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )

    result_text = response.text
    classified = json.loads(result_text)

    events: list[Event] = []
    now = datetime.now(UTC)
    for item in classified:
        try:
            event = Event(
                id=_event_id(item["title"], item["date_start"], item.get("location", "")),
                title=item["title"],
                description=item.get("description", ""),
                date_start=item["date_start"],
                date_end=item.get("date_end"),
                time=item.get("time", ""),
                location=item.get("location", ""),
                address=item.get("address", ""),
                category=item["category"],
                tags=item.get("tags", []),
                urls=item.get("urls", []),
                image_url=item.get("image_url", ""),
                sources=item.get("sources", []),
                classified_at=now,
            )
            events.append(event)
        except (KeyError, ValueError):
            logger.warning("Skipping malformed event from LLM: %s", item)

    return events


def _merge_duplicates(events: list[Event]) -> list[Event]:
    """Merge events with the same ID (same title + date + location).

    Combines URLs and sources from duplicates, keeps the longest description.
    """
    seen: dict[str, Event] = {}
    for event in events:
        if event.id not in seen:
            seen[event.id] = event
        else:
            existing = seen[event.id]
            # Merge URLs and sources
            merged_urls = list(dict.fromkeys(existing.urls + event.urls))
            merged_sources = list(dict.fromkeys(existing.sources + event.sources))
            merged_tags = list(dict.fromkeys(existing.tags + event.tags))
            # Keep longest description
            description = (
                event.description
                if len(event.description) > len(existing.description)
                else existing.description
            )
            # Keep image if existing has none
            image_url = existing.image_url or event.image_url

            seen[event.id] = existing.model_copy(
                update={
                    "urls": merged_urls,
                    "sources": merged_sources,
                    "tags": merged_tags,
                    "description": description,
                    "image_url": image_url,
                },
            )

    return list(seen.values())
