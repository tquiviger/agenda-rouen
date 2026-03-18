"""Publish classified events as static JSON files to S3."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from agenda_rouen.models import Event


def _group_by_date(events: list[Event]) -> dict[str, list[dict]]:
    """Group events by start date."""
    by_date: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        key = event.date_start.isoformat()
        by_date[key].append(event.model_dump(mode="json"))
    return dict(by_date)


def _group_by_category(events: list[Event]) -> dict[str, list[dict]]:
    """Group events by category."""
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        by_cat[event.category.value].append(event.model_dump(mode="json"))
    return dict(by_cat)


def publish_to_s3(
    events: list[Event],
    bucket: str,
    prefix: str = "api/v1",
) -> list[str]:
    """Generate and upload JSON files to S3. Returns list of uploaded keys.

    Generates:
      - {prefix}/events.json           — all events
      - {prefix}/dates/{date}.json     — events for a specific date
      - {prefix}/categories/{cat}.json — events for a specific category
    """
    s3 = boto3.client("s3")
    uploaded: list[str] = []

    def _put(key: str, data: object) -> None:
        body = json.dumps(data, ensure_ascii=False, default=str)
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=body.encode(),
            ContentType="application/json",
            CacheControl="public, max-age=3600",
        )
        uploaded.append(key)

    # All events
    all_events = [e.model_dump(mode="json") for e in events]
    _put(f"{prefix}/events.json", all_events)

    # By date
    for date_str, date_events in _group_by_date(events).items():
        _put(f"{prefix}/dates/{date_str}.json", date_events)

    # By category
    for cat, cat_events in _group_by_category(events).items():
        _put(f"{prefix}/categories/{cat}.json", cat_events)

    return uploaded
