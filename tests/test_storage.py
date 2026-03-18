"""Tests for S3 storage (using moto mock)."""

import json
from datetime import date, datetime

import boto3
from moto import mock_aws

from agenda_rouen.models import Category, Event
from agenda_rouen.storage.s3 import publish_to_s3


def _make_event(title: str, date_start: date, category: Category) -> Event:
    return Event(
        id=f"test-{title[:8]}",
        title=title,
        date_start=date_start,
        category=category,
        urls=["https://example.com"],
        sources=["test"],
        classified_at=datetime(2026, 3, 18, 12, 0),
    )


@mock_aws
def test_publish_creates_expected_files() -> None:
    s3 = boto3.client("s3", region_name="eu-west-3")
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-3"},
    )

    events = [
        _make_event("Concert Rock", date(2026, 3, 20), Category.MUSIC),
        _make_event("Match Rugby", date(2026, 3, 20), Category.SPORT),
        _make_event("Expo Art", date(2026, 3, 21), Category.EXHIBITION),
    ]

    keys = publish_to_s3(events, bucket="test-bucket")

    # events.json + 2 date files + 3 category files = 6
    assert len(keys) == 6

    # Verify events.json content
    obj = s3.get_object(Bucket="test-bucket", Key="api/v1/events.json")
    data = json.loads(obj["Body"].read())
    assert len(data) == 3

    # Verify date grouping
    obj = s3.get_object(Bucket="test-bucket", Key="api/v1/dates/2026-03-20.json")
    data = json.loads(obj["Body"].read())
    assert len(data) == 2


@mock_aws
def test_publish_empty_list() -> None:
    s3 = boto3.client("s3", region_name="eu-west-3")
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-3"},
    )

    keys = publish_to_s3([], bucket="test-bucket")
    assert keys == ["api/v1/events.json"]
