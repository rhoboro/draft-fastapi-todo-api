from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from freezegun import freeze_time

from app.utils.datetime import to_utc, utcnow


class TestToUtc:
    def test_to_utc(self) -> None:
        dt = datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)
        expected = dt
        actual = to_utc(dt)
        assert actual == expected

    def test_to_utc_no_timezone(self) -> None:
        dt = datetime(2026, 1, 2, 3, 4)
        expected = datetime(
            2026, 1, 2, 3, 4, tzinfo=timezone.utc
        )
        actual = to_utc(dt)
        assert actual == expected

    def test_to_utc_jst(self) -> None:
        dt = datetime(
            2026,
            1,
            2,
            3,
            4,
            tzinfo=ZoneInfo(key="Asia/Tokyo"),
        )
        expected = datetime(
            2026, 1, 1, 18, 4, tzinfo=timezone.utc
        )
        actual = to_utc(dt)
        assert actual == expected


@freeze_time("2026-01-02 03:04:00", tz_offset=0)
def test_utcnow() -> None:
    expected = datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)
    actual = utcnow()
    assert actual == expected
