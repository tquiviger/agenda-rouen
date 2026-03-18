"""Quick script to test scrapers against real sites."""

import asyncio
import logging

from dotenv import load_dotenv

from agenda_rouen.scrapers.jds import JdsScraper
from agenda_rouen.scrapers.openagenda import create_openagenda_scrapers
from agenda_rouen.scrapers.rouen_on_est import RouenOnEstScraper

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


async def main() -> None:
    # Test OpenAgenda scrapers
    for scraper in create_openagenda_scrapers():
        async with scraper:
            events = await scraper.scrape()
            print(f"\n=== {scraper.name}: {len(events)} events ===")
            for e in events[:3]:
                print(f"  - {e.title} | {e.date_start} | {e.location}")

    # Test RouenOnEst scraper (Google Calendar)
    async with RouenOnEstScraper() as scraper:
        events = await scraper.scrape()
        print(f"\n=== {scraper.name}: {len(events)} events ===")
        for e in events[:5]:
            print(f"  - {e.title} | {e.date_start} | {e.location} | {e.raw_category}")

    # Test JDS scraper
    async with JdsScraper() as scraper:
        events = await scraper.scrape()
        print(f"\n=== {scraper.name}: {len(events)} events ===")
        for e in events[:5]:
            print(f"  - {e.title} | {e.date_start} | {e.location} | {e.raw_category}")


if __name__ == "__main__":
    asyncio.run(main())
