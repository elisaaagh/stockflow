
import pytest

from api.security import (
    hash_password,
    verify_password
)


def test_password_hashing():
    password = "ExampleSecurePass2026!"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)


def test_incorrect_password():
    password = "ExampleSecurePass2026!"

    hashed = hash_password(password)

    assert not verify_password(
        "WrongPassword2026!",
        hashed
    )


def test_short_password():
    with pytest.raises(ValueError):
        hash_password("short")
