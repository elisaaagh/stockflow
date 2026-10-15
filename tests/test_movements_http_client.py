
import pytest

from services import movements_api
from services.api_client import APIClientError


# ==========================================
# GET MOVEMENTS
# ==========================================

def test_get_movements_from_api(monkeypatch):

    calls = []

    def fake_request(method, endpoint, **kwargs):
        calls.append({
            "method": method,
            "endpoint": endpoint,
            **kwargs
        })

        return [
            {
                "movement_id": 1,
                "product_id": 1,
                "warehouse_id": 1,
                "movement_type": "IN",
                "quantity": "10.00"
            }
        ]

    monkeypatch.setattr(
        movements_api,
        "get_access_token",
        lambda: "test-token"
    )

    monkeypatch.setattr(
        movements_api,
        "api_request",
        fake_request
    )

    result = movements_api.get_movements_from_api()

    assert len(result) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["endpoint"] == "/api/movements"
    assert calls[0]["token"] == "test-token"


# ==========================================
# REGISTER MOVEMENT
# ==========================================

def test_register_movement_from_api(monkeypatch):

    calls = []

    def fake_request(method, endpoint, **kwargs):
        calls.append({
            "method": method,
            "endpoint": endpoint,
            **kwargs
        })

        return {"movement_id": 25}

    monkeypatch.setattr(
        movements_api,
        "get_access_token",
        lambda: "test-token"
    )

    monkeypatch.setattr(
        movements_api,
        "api_request",
        fake_request
    )

    result = movements_api.register_movement_from_api(
        product_id=1,
        warehouse_id=1,
        movement_type="IN",
        quantity=5,
        notes="Test movement"
    )

    assert result["movement_id"] == 25
    assert calls[0]["method"] == "POST"
    assert calls[0]["endpoint"] == "/api/movements"
    assert calls[0]["token"] == "test-token"

    assert calls[0]["json_data"] == {
        "product_id": 1,
        "warehouse_id": 1,
        "movement_type": "IN",
        "quantity": "5",
        "notes": "Test movement"
    }


# ==========================================
# INSUFFICIENT STOCK ERROR
# ==========================================

def test_insufficient_stock_http_error(monkeypatch):

    def fake_request(method, endpoint, **kwargs):
        raise APIClientError(
            "Insufficient stock.",
            status_code=409
        )

    monkeypatch.setattr(
        movements_api,
        "get_access_token",
        lambda: "test-token"
    )

    monkeypatch.setattr(
        movements_api,
        "api_request",
        fake_request
    )

    with pytest.raises(APIClientError) as error:
        movements_api.register_movement_from_api(
            product_id=1,
            warehouse_id=1,
            movement_type="OUT",
            quantity=100,
            notes="Test insufficient stock"
        )

    assert error.value.status_code == 409
