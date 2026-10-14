from datetime import datetime, timezone, timedelta
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from src.creator_ttl_service import CreatorObject, expired_objects


def test_ttl_marks_only_old_throwaways():
    now = datetime(2026, 1, 2, tzinfo=timezone.utc)
    objects = [
        CreatorObject("draft/old.mp4", now - timedelta(hours=25), "video"),
        CreatorObject("subscriber/new.json", now - timedelta(hours=2), "update"),
    ]
    result = expired_objects(objects, now, timedelta(hours=24))
    assert [item.key for item in result if item.expired] == ["draft/old.mp4"]
