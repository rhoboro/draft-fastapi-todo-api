from datetime import datetime, timezone


def to_utc(utc_or_native: datetime) -> datetime:
    if _is_aware(utc_or_native):
        return utc_or_native.astimezone(timezone.utc)

    return utc_or_native.replace(tzinfo=timezone.utc)


def _is_aware(v: datetime) -> bool:
    # https://docs.python.org/ja/3.13/library/datetime.html#determining-if-an-object-is-aware-or-naive
    if v.tzinfo is not None:
        if v.tzinfo.utcoffset(v) is not None:
            return True

    return False
