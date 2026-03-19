"""Classify events by mapping raw categories to our unified taxonomy via Gemini."""


from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import UTC, datetime

from google import genai

from agenda_rouen.models import Category, Event, RawEvent

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
Tu es un assistant spécialisé dans la classification d'événements culturels et sportifs \
à Rouen et ses environs.

Catégories disponibles : {categories}

Tu reçois une liste de catégories brutes provenant de différentes sources. \
Pour chaque catégorie brute, assigne la catégorie la plus pertinente parmi la liste ci-dessus.

Réponds en JSON strict (pas de markdown) : un objet dont les clés sont les catégories brutes \
et les valeurs sont les catégories de notre taxonomie.

Exemple :
{{"Concerts à Rouen": "musique", "Spectacles à Rouen": "spectacles", "Courses à Rouen": "sport"}}
"""

# Events with an empty raw_category need classification by title
_TITLE_CLASSIFY_PROMPT = """\
Tu es un assistant spécialisé dans la classification d'événements culturels et sportifs \
à Rouen et ses environs.

Catégories disponibles : {categories}

Tu reçois une liste de titres d'événements. \
Pour chaque titre, assigne la catégorie la plus pertinente parmi la liste ci-dessus.

Réponds en JSON strict (pas de markdown) : un objet dont les clés sont les titres \
et les valeurs sont les catégories de notre taxonomie.
"""

_TITLE_BATCH_SIZE = 100

# Static fallback mapping for known raw categories (avoids LLM call when quota is exhausted)
_STATIC_CAT_MAPPING: dict[str, str] = {
    "Ateliers à Rouen": "ateliers",
    "Balades à Rouen": "famille",
    "Bien-être à Rouen": "autre",
    "Carnaval à Rouen": "festival",
    "Chanson française à Rouen": "musique",
    "Cinéma à Rouen": "cinéma",
    "Concerts à Rouen": "musique",
    "Conférences à Rouen": "conférences",
    "Courses à Rouen": "sport",
    "Danse à Rouen": "spectacles",
    "Electro à Rouen": "musique",
    "Expos à Rouen": "expositions",
    "Festival à Rouen": "festival",
    "Foires à Rouen": "famille",
    "Gastronomie à Rouen": "gastronomie",
    "Humour à Rouen": "spectacles",
    "Lotos à Rouen": "autre",
    "Manifestations à Rouen": "autre",
    "Marchés à Rouen": "gastronomie",
    "Musique classique à Rouen": "musique",
    "Pop / folk à Rouen": "musique",
    "Rap à Rouen": "musique",
    "Reggae à Rouen": "musique",
    "Rock / metal à Rouen": "musique",
    "Spectacle musical à Rouen": "spectacles",
    "Spectacles à Rouen": "spectacles",
    "Théâtre à Rouen": "spectacles",
    "Visites à Rouen": "famille",
    "Culture & Expos": "expositions",
    "Dates majeures": "autre",
    "Sports & Compétitions": "sport",
    "Grands événements": "festival",
    "Animations & Spectacles": "spectacles",
}


def _event_id(title: str, date_start: str, location: str) -> str:
    """Generate a deterministic ID from key event fields."""
    raw = f"{title.lower().strip()}|{date_start}|{location.lower().strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _get_client() -> genai.Client:
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


async def classify(
    raw_events: list[RawEvent],
    *,
    model: str = "gemini-2.5-flash",
) -> list[Event]:
    """Classify raw events into our unified taxonomy.

    Strategy:
    1. Collect unique raw_category values → ask Gemini for a mapping to our taxonomy.
    2. For events without raw_category, classify by title in batches.
    3. Apply the mapping to build Event objects.
    """
    if not raw_events:
        return []

    categories_str = ", ".join(c.value for c in Category)

    # Step 1: map raw categories using static fallback, call Gemini only for unknown ones
    cat_mapping: dict[str, str] = dict(_STATIC_CAT_MAPPING)
    unique_cats = {e.raw_category for e in raw_events if e.raw_category}
    unknown_cats = unique_cats - set(cat_mapping)

    client: genai.Client | None = None

    if unknown_cats:
        logger.info("Unknown categories to classify via LLM: %s", unknown_cats)
        try:
            client = _get_client()
            llm_mapping = _classify_categories(client, unknown_cats, categories_str, model)
            cat_mapping.update(llm_mapping)
        except Exception:
            logger.exception("Failed to classify unknown categories, defaulting to 'autre'")
    else:
        logger.info("All %d raw categories resolved from static mapping", len(unique_cats))

    # Step 2: classify events with no raw_category by title
    no_cat_events = [e for e in raw_events if not e.raw_category]
    title_mapping: dict[str, str] = {}

    if no_cat_events:
        unique_titles = list({e.title for e in no_cat_events})
        logger.info("Classifying %d unique titles (no raw_category)", len(unique_titles))

        if client is None:
            try:
                client = _get_client()
            except Exception:
                logger.warning(
                    "Cannot create Gemini client, all titleless events default to 'autre'"
                )

        if client is not None:
            for i in range(0, len(unique_titles), _TITLE_BATCH_SIZE):
                batch = unique_titles[i : i + _TITLE_BATCH_SIZE]
                try:
                    batch_mapping = _classify_titles(client, batch, categories_str, model)
                    title_mapping.update(batch_mapping)
                except Exception:
                    logger.exception(
                        "Failed to classify title batch %d, defaulting to 'autre'",
                        i // _TITLE_BATCH_SIZE + 1,
                    )

    # Step 3: build Event objects, dedup by (normalized title + date)
    now = datetime.now(UTC)
    seen: set[tuple[str, str]] = set()
    events: list[Event] = []

    # Sort by longest description first so dedup keeps the richest entry
    sorted_raw = sorted(raw_events, key=lambda e: len(e.description), reverse=True)

    for raw in sorted_raw:
        dedup_key = (raw.title.lower().strip(), str(raw.date_start))
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        # Resolve category
        if raw.raw_category:
            cat_value = cat_mapping.get(raw.raw_category, Category.OTHER.value)
        else:
            cat_value = title_mapping.get(raw.title, Category.OTHER.value)

        try:
            category = Category(cat_value)
        except ValueError:
            category = Category.OTHER

        eid = _event_id(raw.title, str(raw.date_start), raw.location)

        events.append(Event(
            id=eid,
            title=raw.title,
            description=raw.description,
            date_start=raw.date_start,
            date_end=raw.date_end,
            time=raw.time,
            location=raw.location,
            address=raw.address,
            category=category,
            tags=[],
            urls=[raw.url] if raw.url else [],
            image_url=raw.image_url,
            sources=[raw.source],
            classified_at=now,
        ))

    logger.info(
        "Classified %d raw → %d unique events (%d via category, %d via title)",
        len(raw_events),
        len(events),
        len(raw_events) - len(no_cat_events),
        len(no_cat_events),
    )
    return events


def _classify_categories(
    client: genai.Client,
    raw_categories: set[str],
    categories_str: str,
    model: str,
) -> dict[str, str]:
    """Ask Gemini to map raw category names to our taxonomy. Single API call."""
    system = _SYSTEM_PROMPT.format(categories=categories_str)
    content = json.dumps(sorted(raw_categories), ensure_ascii=False)

    response = client.models.generate_content(
        model=model,
        contents=content,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=4096,
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )

    return json.loads(response.text)


def _classify_titles(
    client: genai.Client,
    titles: list[str],
    categories_str: str,
    model: str,
) -> dict[str, str]:
    """Ask Gemini to classify event titles into our taxonomy."""
    system = _TITLE_CLASSIFY_PROMPT.format(categories=categories_str)
    content = json.dumps(titles, ensure_ascii=False)

    response = client.models.generate_content(
        model=model,
        contents=content,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=16384,
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )

    return json.loads(response.text)
