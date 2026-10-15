
from fastapi.testclient import TestClient

from api.main import app
from api.security import hash_password
import api.routers.auth as auth_router
import api.dependencies.auth as auth_dependencies


client = TestClient(app)

TEST_PASSWORD = "ExampleSecurePass2026!"


def sample_user():
    return {
        "user_id": 1,
        "username": "testadmin",
        "password_hash": hash_password(TEST_PASSWORD),
        "role": "admin",
        "is_active": True
    }


def test_login_success(monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "get_user_by_username",
        lambda username: sample_user()
    )

    monkeypatch.setattr(
        auth_router,
        "create_access_token",
        lambda user_id: "mock-access-token"
    )

    response = client.post(
        "/api/auth/login",
        data={
            "username": "testadmin",
            "password": TEST_PASSWORD
        }
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "mock-access-token"
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "get_user_by_username",
        lambda username: sample_user()
    )

    response = client.post(
        "/api/auth/login",
        data={
            "username": "testadmin",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401


def test_me_without_token():
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_with_valid_token(monkeypatch):
    monkeypatch.setattr(
        auth_dependencies,
        "decode_access_token",
        lambda token: 1
    )

    monkeypatch.setattr(
        auth_dependencies,
        "get_user_by_id",
        lambda user_id: sample_user()
    )

    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": "Bearer mock-access-token"
        }
    )

    assert response.status_code == 200
    assert response.json()["username"] == "testadmin"
    assert response.json()["role"] == "admin"
    assert "password_hash" not in response.json()
