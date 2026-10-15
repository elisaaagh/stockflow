
from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from api.main import app
import api.routers.movements as movements_router

from database.movements import StockMovementError
from tests.auth_helpers import authenticated_as

client = TestClient(app)


def test_get_movements(monkeypatch, login_as):
    login_as("viewer")

    monkeypatch.setattr(
        movements_router,
        "get_movements",
        lambda: [{
            "movement_id": 1,
            "created_at": datetime.now(timezone.utc),
            "sku": "TEST001",
            "product": "Test Product",
            "warehouse": "Main Warehouse",
            "movement_type": "IN",
            "quantity": Decimal("5.00"),
            "unit": "Pieza",
            "notes": "Test movement"
        }]
    )

    response = client.get("/api/movements")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_movement(monkeypatch):

    monkeypatch.setattr(
        movements_router,
        "register_movement",
        lambda **kwargs: 25
    )

    with authenticated_as("operator"):
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


def test_insufficient_stock(monkeypatch, login_as):
    login_as("operator")

    def fake_register(**kwargs):
        raise StockMovementError(
            "Insufficient stock. Available: 2.00"
        )

    monkeypatch.setattr(
        movements_router,
        "register_movement",
        fake_register
    )

    response = client.post(
        "/api/movements",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "movement_type": "OUT",
            "quantity": 10
        }
    )

    assert response.status_code == 409


def test_invalid_quantity(login_as):
    login_as("operator")

    response = client.post(
        "/api/movements",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "movement_type": "IN",
            "quantity": -5
        }
    )

    assert response.status_code == 422


def test_invalid_movement_type(login_as):
    login_as("operator")

    response = client.post(
        "/api/movements",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "movement_type": "TRANSFER",
            "quantity": 5
        }
    )

    assert response.status_code == 422
