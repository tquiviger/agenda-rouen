"""AWS Lambda handler — entry point for the scheduled scraping pipeline."""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any

import boto3

from agenda_rouen.classifier.llm import classify
from agenda_rouen.models import RawEvent
from agenda_rouen.scrapers.base import BaseScraper
from agenda_rouen.scrapers.jds import JdsScraper
from agenda_rouen.scrapers.openagenda import create_openagenda_scrapers
from agenda_rouen.scrapers.rouen_on_est import RouenOnEstScraper
from agenda_rouen.storage.s3 import publish_to_s3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BUCKET = os.environ.get("EVENTS_BUCKET", "agenda-rouen-events")
CLOUDFRONT_DISTRIBUTION_ID = os.environ.get("CLOUDFRONT_DISTRIBUTION_ID", "")


def _build_scrapers() -> list[BaseScraper]:
    """Instantiate all active scrapers."""
    scrapers: list[BaseScraper] = [JdsScraper(), RouenOnEstScraper()]
    scrapers.extend(create_openagenda_scrapers())
    return scrapers


async def _run_pipeline() -> dict[str, Any]:
    """Run the full scrape → classify → publish pipeline."""
    all_raw: list[RawEvent] = []
    scrapers = _build_scrapers()

    # Scrape all sources concurrently
    async def _scrape_one(scraper: BaseScraper) -> list[RawEvent]:
        try:
            async with scraper:
                events = await scraper.scrape()
                logger.info("Scraped %d events from %s", len(events), scraper.name)
                return events
        except Exception:
            logger.exception("Failed to scrape %s", scraper.name)
            return []

    results = await asyncio.gather(*[_scrape_one(s) for s in scrapers])
    for events in results:
        all_raw.extend(events)

    logger.info("Total raw events: %d", len(all_raw))

    # Classify via LLM
    classified = await classify(all_raw)
    logger.info("Classified events: %d", len(classified))

    # Publish to S3
    keys = publish_to_s3(classified, bucket=BUCKET)
    logger.info("Published %d files to S3", len(keys))

    # Invalidate CloudFront cache
    if CLOUDFRONT_DISTRIBUTION_ID:
        _invalidate_cloudfront(CLOUDFRONT_DISTRIBUTION_ID)

    return {
        "raw_count": len(all_raw),
        "classified_count": len(classified),
        "files_published": len(keys),
    }


def _invalidate_cloudfront(distribution_id: str) -> None:
    """Create a CloudFront invalidation for the API paths."""
    try:
        client = boto3.client("cloudfront")
        client.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                "Paths": {"Quantity": 1, "Items": ["/api/v1/*"]},
                "CallerReference": str(int(time.time())),
            },
        )
        logger.info("CloudFront invalidation created for %s", distribution_id)
    except Exception:
        logger.exception("Failed to invalidate CloudFront cache")


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """AWS Lambda entry point."""
    result = asyncio.run(_run_pipeline())
    return {"statusCode": 200, "body": result}
