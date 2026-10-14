
from decimal import Decimal

from fastapi.testclient import TestClient
from psycopg.errors import UniqueViolation

from api.main import app
import api.routers.products as products_router


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

    response = client.get("/api/products")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["sku"] == "TEST001"


def test_get_product_not_found(monkeypatch):
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


def test_invalid_stock():
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
