from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Iterable, List


@dataclass(frozen=True)
class CreatorObject:
    key: str
    created_at: datetime
    kind: str


@dataclass(frozen=True)
class SweepDecision:
    key: str
    expired: bool


def expired_objects(objects: Iterable[CreatorObject], now: datetime, ttl: timedelta) -> List[SweepDecision]:
    return [SweepDecision(item.key, now - item.created_at >= ttl) for item in objects]


def run_sweep(client, bucket: str, ttl: timedelta, now: datetime | None = None) -> List[str]:
    current = now or datetime.now(timezone.utc)
    data = client.list_objects(bucket) or {}
    items = data.get("items", [])
    parsed = []
    for item in items:
        created = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        parsed.append(CreatorObject(item["key"], created, item.get("kind", "asset")))
    doomed = [d.key for d in expired_objects(parsed, current, ttl) if d.expired]
    for key in doomed:
        client.delete_object(bucket, key)
    return doomed

