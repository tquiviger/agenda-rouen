"""Quick test: scrape a few events then classify via Gemini."""

import asyncio
import json
import logging

from dotenv import load_dotenv

from agenda_rouen.classifier.llm import classify_and_dedup
from agenda_rouen.scrapers.openagenda import OpenAgendaScraper

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


async def main() -> None:
    # Grab a small sample from OpenAgenda Rouen (smallest agenda)
    scraper = OpenAgendaScraper(agenda_name="openagenda_rouen", agenda_uid=11174431)
    async with scraper:
        raw_events = await scraper.scrape()

    print(f"\n--- Raw events: {len(raw_events)} ---")
    for e in raw_events[:5]:
        print(f"  {e.title} | {e.date_start} | {e.source}")

    # Classify via Gemini
    print("\n--- Classifying via Gemini Flash... ---")
    classified = await classify_and_dedup(raw_events[:10])

    print(f"\n--- Classified events: {len(classified)} ---")
    for e in classified:
        print(f"  [{e.category.value}] {e.title} | {e.date_start} | tags={e.tags}")

    # Show one full event as JSON
    if classified:
        print("\n--- Sample event JSON ---")
        print(json.dumps(classified[0].model_dump(mode="json"), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
