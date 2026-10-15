
from contextlib import contextmanager

from api.main import app
from api.dependencies.auth import get_current_user


def fake_user(role="admin"):
    """Return a simulated authenticated user."""
    return {
        "user_id": 1,
        "username": "testuser",
        "role": role,
        "is_active": True
    }


@contextmanager
def authenticated_as(role="admin"):
    """Temporarily override authentication for an API test."""

    previous = app.dependency_overrides.get(
        get_current_user
    )

    app.dependency_overrides[get_current_user] = (
        lambda: fake_user(role)
    )

    try:
        yield

    finally:
        if previous is None:
            app.dependency_overrides.pop(
                get_current_user,
                None
            )
        else:
            app.dependency_overrides[get_current_user] = previous
