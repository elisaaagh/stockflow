
from decimal import Decimal

from fastapi.testclient import TestClient
from psycopg.errors import UniqueViolation

from api.main import app
import api.routers.products as products_router
from tests.auth_helpers import authenticated_as

client = TestClient(app)


SAMPLE_PRODUCT = {
    "product_id": 1,
    "sku": "TEST001",
    "name": "Test Product",
    "description": "Sample product",
    "unit": "Pieza",
    "min_stock": Decimal("10.00"),
    "is_active": True
}


def test_get_products(monkeypatch):
    monkeypatch.setattr(
        products_router,
        "get_all_products",
        lambda: [SAMPLE_PRODUCT]
    )

    with authenticated_as("admin"):
        response = client.get("/api/products")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["sku"] == "TEST001"


def test_get_product_not_found(monkeypatch, login_as):
    login_as("admin")
    monkeypatch.setattr(
        products_router,
        "get_product_by_id",
        lambda product_id: None
    )

    response = client.get("/api/products/999")

    assert response.status_code == 404


def test_create_product(monkeypatch):
    monkeypatch.setattr(
        products_router,
        "create_product",
        lambda **kwargs: 1
    )

    monkeypatch.setattr(
        products_router,
        "get_product_by_id",
        lambda product_id: SAMPLE_PRODUCT
    )

    with authenticated_as("admin"):
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


def test_invalid_stock(login_as):
    login_as("admin")
    response = client.post(
        "/api/products",
        json={
            "sku": "INVALID001",
            "name": "Invalid Product",
            "unit": "Pieza",
            "min_stock": -10
        }
    )

    assert response.status_code == 422

def test_put_product(monkeypatch, login_as):
    login_as("admin")
    calls = []

    monkeypatch.setattr(
        products_router,
        "get_product_by_id",
        lambda product_id: SAMPLE_PRODUCT
    )

    def fake_update_product(**kwargs):
        calls.append(kwargs)
        return True

    monkeypatch.setattr(
        products_router,
        "update_product",
        fake_update_product
    )

    response = client.put(
        "/api/products/1",
        json={
            "name": "Updated Product",
            "description": "Updated description",
            "unit": "Pieza",
            "min_stock": 20
        }
    )

    assert response.status_code == 200
    assert calls[0]["name"] == "Updated Product"
    assert calls[0]["min_stock"] == 20


def test_patch_product(monkeypatch, login_as):
    login_as("admin")
    calls = []

    monkeypatch.setattr(
        products_router,
        "get_product_by_id",
        lambda product_id: SAMPLE_PRODUCT
    )

    def fake_update_product(**kwargs):
        calls.append(kwargs)
        return True

    monkeypatch.setattr(
        products_router,
        "update_product",
        fake_update_product
    )

    response = client.patch(
        "/api/products/1",
        json={"min_stock": 30}
    )

    assert response.status_code == 200
    assert calls[0]["name"] == SAMPLE_PRODUCT["name"]
    assert calls[0]["min_stock"] == 30
