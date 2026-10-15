
import pytest
import api.routers.products as products_router
import api.routers.movements as movements_router

from fastapi.testclient import TestClient

from api.main import app
from api.dependencies.auth import get_current_user


client = TestClient(app)


# ==========================================
# TEST USERS
# ==========================================

def fake_user(role):
    return {
        "user_id": 1,
        "username": "testuser",
        "role": role,
        "is_active": True
    }


@pytest.fixture(autouse=True)
def clean_auth_overrides():
    """Restore auth overrides after each test."""
    previous = app.dependency_overrides.get(get_current_user)

    yield

    if previous is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = previous


def login_as(role):
    """Simulate a user with a specific role."""
    app.dependency_overrides[get_current_user] = (
        lambda: fake_user(role)
    )


# ==========================================
# PRODUCTS — AUTHENTICATION
# ==========================================

def test_products_without_token():
    response = client.get("/api/products")

    assert response.status_code == 401


# ==========================================
# PRODUCTS — ADMIN ONLY
# ==========================================

@pytest.mark.parametrize(
    "role",
    ["operator", "viewer"]
)
def test_create_product_forbidden(role):
    login_as(role)

    response = client.post(
        "/api/products",
        json={
            "sku": "TEST001",
            "name": "Test Product",
            "unit": "Pieza",
            "min_stock": 10
        }
    )

    assert response.status_code == 403


# ==========================================
# MOVEMENTS — OPERATOR OR ADMIN
# ==========================================

def test_movement_forbidden_for_viewer():
    login_as("viewer")

    response = client.post(
        "/api/movements",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "movement_type": "IN",
            "quantity": 5
        }
    )

    assert response.status_code == 403


# ==========================================
# INVENTORY — AUTHENTICATION
# ==========================================

def test_inventory_without_token():
    response = client.get("/api/inventory")

    assert response.status_code == 401


def test_movement_without_token():
    response = client.post(
        "/api/movements",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "movement_type": "IN",
            "quantity": 5
        }
    )

    assert response.status_code == 401

# ==========================================
# AUTHORIZED ACCESS TESTS
# ==========================================

SAMPLE_PRODUCT = {
    "product_id": 1,
    "sku": "TEST001",
    "name": "Test Product",
    "description": None,
    "unit": "Pieza",
    "min_stock": 10,
    "is_active": True
}


# ==========================================
# ADMIN CAN CREATE PRODUCTS
# ==========================================

def test_admin_can_create_product(monkeypatch):
    login_as("admin")

    def fake_create_product(**kwargs):
        return 1

    monkeypatch.setattr(
        products_router,
        "create_product",
        fake_create_product
    )

    monkeypatch.setattr(
        products_router,
        "get_product_by_id",
        lambda product_id: SAMPLE_PRODUCT
    )

    response = client.post(
        "/api/products",
        json={
            "sku": "TEST001",
            "name": "Test Product",
            "unit": "Pieza",
            "min_stock": 10
        }
    )

    assert response.status_code == 201
    assert response.json()["sku"] == "TEST001"


# ==========================================
# ADMIN / OPERATOR CAN REGISTER MOVEMENTS
# ==========================================

@pytest.mark.parametrize(
    "role",
    ["admin", "operator"]
)
def test_authorized_movement(monkeypatch, role):
    login_as(role)

    def fake_register_movement(**kwargs):
        return 25

    monkeypatch.setattr(
        movements_router,
        "register_movement",
        fake_register_movement
    )

    response = client.post(
        "/api/movements",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "movement_type": "IN",
            "quantity": 5
        }
    )

    assert response.status_code == 201
    assert response.json()["movement_id"] == 25


# ==========================================
# VIEWER CAN READ PRODUCTS
# ==========================================

def test_viewer_can_read_products(monkeypatch):
    login_as("viewer")

    monkeypatch.setattr(
        products_router,
        "get_all_products",
        lambda: [SAMPLE_PRODUCT]
    )

    response = client.get("/api/products")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["sku"] == "TEST001"


# ==========================================
# VIEWER CAN READ MOVEMENTS
# ==========================================

def test_viewer_can_read_movements(monkeypatch):
    login_as("viewer")

    monkeypatch.setattr(
        movements_router,
        "get_movements",
        lambda: []
    )

    response = client.get("/api/movements")

    assert response.status_code == 200
    assert response.json() == []
