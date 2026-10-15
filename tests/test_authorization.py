
import pytest

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from api.dependencies.auth import (
    get_current_user,
    require_admin,
    require_operator,
    require_viewer
)


authorization_app = FastAPI()


@authorization_app.get("/admin")
def admin_area(
    user: dict = Depends(require_admin)
):
    return {"username": user["username"]}


@authorization_app.post("/movements")
def operator_area(
    user: dict = Depends(require_operator)
):
    return {"username": user["username"]}


@authorization_app.get("/inventory")
def viewer_area(
    user: dict = Depends(require_viewer)
):
    return {"username": user["username"]}


client = TestClient(authorization_app)


def fake_user(role):
    return {
        "user_id": 1,
        "username": "testuser",
        "role": role,
        "is_active": True
    }


@pytest.mark.parametrize(
    "role,expected",
    [
        ("admin", 200),
        ("operator", 403),
        ("viewer", 403)
    ]
)
def test_admin_permissions(role, expected):
    authorization_app.dependency_overrides[get_current_user] = (
        lambda: fake_user(role)
    )

    try:
        response = client.get("/admin")
        assert response.status_code == expected
    finally:
        authorization_app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "role,expected",
    [
        ("admin", 200),
        ("operator", 200),
        ("viewer", 403)
    ]
)
def test_operator_permissions(role, expected):
    authorization_app.dependency_overrides[get_current_user] = (
        lambda: fake_user(role)
    )

    try:
        response = client.post("/movements")
        assert response.status_code == expected
    finally:
        authorization_app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "role,expected",
    [
        ("admin", 200),
        ("operator", 200),
        ("viewer", 200)
    ]
)
def test_viewer_permissions(role, expected):
    authorization_app.dependency_overrides[get_current_user] = (
        lambda: fake_user(role)
    )

    try:
        response = client.get("/inventory")
        assert response.status_code == expected
    finally:
        authorization_app.dependency_overrides.clear()


def test_missing_token():
    response = client.get("/admin")
    assert response.status_code == 401
