
from fastapi.testclient import TestClient

from api.main import app
import api.routers.inventory as inventory_router
from tests.auth_helpers import authenticated_as

client = TestClient(app)


SAMPLE_INVENTORY = [
    {
        "product_id": 1,
        "sku": "TEST001",
        "name": "Test Product",
        "warehouse_id": 1,
        "warehouse": "Main Warehouse",
        "quantity": 5,
        "min_stock": 10,
        "stock_status": "LOW",
        "is_active": True
    },
    {
        "product_id": 1,
        "sku": "TEST001",
        "name": "Test Product",
        "warehouse_id": 2,
        "warehouse": "Secondary Warehouse",
        "quantity": 20,
        "min_stock": 10,
        "stock_status": "OK",
        "is_active": True
    }
]


def test_get_warehouses(monkeypatch, login_as):
    login_as("viewer")
    monkeypatch.setattr(
        inventory_router,
        "get_warehouses",
        lambda: [
            {
                "warehouse_id": 1,
                "name": "Main Warehouse",
                "location": "Test City",
                "is_active": True
            }
        ]
    )

    response = client.get("/api/warehouses")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_inventory(monkeypatch, login_as):
    login_as("viewer")
    monkeypatch.setattr(
        inventory_router,
        "get_inventory",
        lambda: SAMPLE_INVENTORY
    )

    with authenticated_as("viewer"):
        response = client.get("/api/inventory")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_inventory_by_warehouse(monkeypatch, login_as):
    login_as("viewer")
    monkeypatch.setattr(
        inventory_router,
        "get_inventory",
        lambda: SAMPLE_INVENTORY
    )

    response = client.get(
        "/api/inventory",
        params={"warehouse_id": 1}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["warehouse_id"] == 1


def test_invalid_warehouse_id(login_as):
    login_as("viewer")
    response = client.get(
        "/api/inventory",
        params={"warehouse_id": -1}
    )

    assert response.status_code == 422


def test_get_low_stock(monkeypatch, login_as):
    login_as("viewer")
    monkeypatch.setattr(
        inventory_router,
        "get_low_stock",
        lambda: [SAMPLE_INVENTORY[0]]
    )

    response = client.get("/api/inventory/low-stock")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["stock_status"] == "LOW"
