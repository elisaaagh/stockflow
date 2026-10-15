
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from api.security import (
    create_access_token,
    decode_access_token
)


@pytest.fixture(autouse=True)
def jwt_settings(monkeypatch):
    monkeypatch.setenv(
        "JWT_SECRET_KEY",
        "test-only-secret-key-with-more-than-32-characters"
    )
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")


def test_valid_jwt():
    token = create_access_token(user_id=7)

    assert decode_access_token(token) == 7


def test_invalid_jwt():
    with pytest.raises(ValueError):
        decode_access_token("invalid-token")


def test_expired_jwt():
    secret = (
        "test-only-secret-key-with-more-than-32-characters"
    )

    now = datetime.now(timezone.utc)

    expired_token = jwt.encode(
        {
            "sub": "7",
            "type": "access",
            "iat": now - timedelta(hours=2),
            "nbf": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1)
        },
        secret,
        algorithm="HS256"
    )

    with pytest.raises(ValueError):
        decode_access_token(expired_token)
