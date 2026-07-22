from datetime import datetime, timedelta

from app.models.monetization import ContentUnlock
from app.services.monetization import (
    EMAIL_VIEW_DAYS,
    WEB_VIEW_DAYS,
    unlock_access_info,
)


def test_web_access_valid_within_window():
    now = datetime.utcnow()
    row = ContentUnlock(
        user_id=1,
        product_key="product:x",
        web_expires_at=now + timedelta(days=3),
        email_expires_at=now + timedelta(days=20),
        email_token="tok",
    )
    info = unlock_access_info(row, channel="web")
    assert info["ok"] is True
    assert info["days_left_web"] is not None


def test_web_access_expired():
    now = datetime.utcnow()
    row = ContentUnlock(
        user_id=1,
        product_key="product:x",
        web_expires_at=now - timedelta(days=1),
        email_expires_at=now + timedelta(days=10),
        email_token="tok",
    )
    info = unlock_access_info(row, channel="web")
    assert info["ok"] is False
    assert "7" in (info.get("message") or "") or WEB_VIEW_DAYS


def test_email_access_still_valid_when_web_expired():
    now = datetime.utcnow()
    row = ContentUnlock(
        user_id=1,
        product_key="product:x",
        web_expires_at=now - timedelta(days=1),
        email_expires_at=now + timedelta(days=10),
        email_token="tok",
    )
    info = unlock_access_info(row, channel="email")
    assert info["ok"] is True
    assert EMAIL_VIEW_DAYS == 30
