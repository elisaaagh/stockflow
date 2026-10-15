
import pytest

from fastapi.testclient import TestClient

from api.main import app
from api.dependencies.auth import get_current_user
import api.routers.users as users_router


client = TestClient(app)


# ==========================================
# TEST USER DATA
# ==========================================

SAMPLE_USER = {
    "user_id": 2,
    "username": "operator_test",
    "role": "operator",
    "is_active": True,
    "created_at": "2026-10-15T10:00:00"
}


def fake_user(role):
    return {
        "user_id": 1,
        "username": "test_admin",
        "role": role,
        "is_active": True
    }


@pytest.fixture(autouse=True)
def clean_auth():
    previous = app.dependency_overrides.get(
        get_current_user
    )

    yield

    if previous is None:
        app.dependency_overrides.pop(
            get_current_user,
            None
        )
    else:
        app.dependency_overrides[get_current_user] = previous


def login_as(role):
    app.dependency_overrides[get_current_user] = (
        lambda: fake_user(role)
    )


# ==========================================
# GET USERS — ADMIN
# ==========================================

def test_admin_can_list_users(monkeypatch):
    login_as("admin")

    monkeypatch.setattr(
        users_router,
        "get_all_users",
        lambda: [SAMPLE_USER]
    )

    response = client.get("/api/users")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["username"] == "operator_test"
    assert "password_hash" not in response.json()[0]


# ==========================================
# GET USERS — FORBIDDEN
# ==========================================

@pytest.mark.parametrize("role", ["operator", "viewer"])
def test_non_admin_cannot_list_users(role):
    login_as(role)

    response = client.get("/api/users")

    assert response.status_code == 403


# ==========================================
# POST USERS — ADMIN
# ==========================================

def test_admin_can_create_user(monkeypatch):
    login_as("admin")

    captured = {}

    def fake_create_user(username, password_hash, role):
        captured["username"] = username
        captured["password_hash"] = password_hash
        captured["role"] = role
        return 2

    monkeypatch.setattr(
        users_router,
        "create_user",
        fake_create_user
    )

    monkeypatch.setattr(
        users_router,
        "get_user_by_id",
        lambda user_id: SAMPLE_USER
    )

    response = client.post(
        "/api/users",
        json={
            "username": "OPERATOR_TEST",
            "password": "SecurePassword123!",
            "role": "operator"
        }
    )

    assert response.status_code == 201
    assert response.json()["username"] == "operator_test"
    assert response.json()["role"] == "operator"

    assert captured["username"] == "operator_test"
    assert captured["role"] == "operator"

    # Password must be hashed before storage
    assert captured["password_hash"] != "SecurePassword123!"
    assert captured["password_hash"].startswith("$argon2")
    assert "password_hash" not in response.json()


# ==========================================
# POST USERS — FORBIDDEN
# ==========================================

@pytest.mark.parametrize("role", ["operator", "viewer"])
def test_non_admin_cannot_create_user(role):
    login_as(role)

    response = client.post(
        "/api/users",
        json={
            "username": "newuser",
            "password": "SecurePassword123!",
            "role": "viewer"
        }
    )

    assert response.status_code == 403


# ==========================================
# USERS — WITHOUT AUTHENTICATION
# ==========================================

@pytest.mark.parametrize("method", ["GET", "POST"])
def test_users_without_token(method):
    if method == "GET":
        response = client.get("/api/users")
    else:
        response = client.post(
            "/api/users",
            json={
                "username": "newuser",
                "password": "SecurePassword123!",
                "role": "viewer"
            }
        )

    assert response.status_code == 401


# ==========================================
# INVALID ROLE
# ==========================================

def test_invalid_role(monkeypatch):
    login_as("admin")

    response = client.post(
        "/api/users",
        json={
            "username": "newuser",
            "password": "SecurePassword123!",
            "role": "superadmin"
        }
    )

    assert response.status_code == 422

# ==========================================
# DUPLICATE USERNAME
# ==========================================

def test_duplicate_username(monkeypatch):
    from psycopg.errors import UniqueViolation

    login_as("admin")

    def fake_create_user(**kwargs):
        raise UniqueViolation("Username already exists.")

    monkeypatch.setattr(
        users_router,
        "create_user",
        fake_create_user
    )

    response = client.post(
        "/api/users",
        json={
            "username": "existinguser",
            "password": "SecurePassword123!",
            "role": "viewer"
        }
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Username already exists."
    )


# ==========================================
# PASSWORD TOO SHORT
# ==========================================

def test_short_user_password():
    login_as("admin")

    response = client.post(
        "/api/users",
        json={
            "username": "newuser",
            "password": "12345",
            "role": "viewer"
        }
    )

    assert response.status_code == 422


# ==========================================
# INVALID USERNAME
# ==========================================

def test_invalid_username():
    login_as("admin")

    response = client.post(
        "/api/users",
        json={
            "username": "invalid user!",
            "password": "SecurePassword123!",
            "role": "viewer"
        }
    )

    assert response.status_code == 422
