from datetime import datetime, timezone

from expiry_radar.checker import days_until, normalize_host


def test_host_normalization_accepts_url_and_case():
    assert normalize_host("HTTPS://Example.COM/path") == "example.com"


def test_days_until_uses_utc_aware_math():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert days_until(datetime(2026, 1, 31, tzinfo=timezone.utc), now) == 30
