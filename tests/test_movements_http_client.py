
import httpx
import pytest

from services import movements_api


def test_get_movements_from_api(monkeypatch):

    def mock_response(request):
        assert request.method == "GET"
        assert request.url.path == "/api/movements"

        return httpx.Response(
            200,
            json=[
                {
                    "movement_id": 1,
                    "movement_type": "IN",
                    "quantity": 5
                }
            ]
        )

    transport = httpx.MockTransport(mock_response)
    real_client = httpx.Client

    monkeypatch.setattr(
        movements_api.httpx,
        "Client",
        lambda **kwargs: real_client(
            transport=transport,
            **kwargs
        )
    )

    result = movements_api.get_movements_from_api()

    assert len(result) == 1
    assert result[0]["movement_id"] == 1


def test_register_movement_from_api(monkeypatch):

    def mock_response(request):
        assert request.method == "POST"
        assert request.url.path == "/api/movements"

        return httpx.Response(
            201,
            json={
                "movement_id": 25,
                "message": "Movement registered."
            }
        )

    transport = httpx.MockTransport(mock_response)
    real_client = httpx.Client

    monkeypatch.setattr(
        movements_api.httpx,
        "Client",
        lambda **kwargs: real_client(
            transport=transport,
            **kwargs
        )
    )

    result = movements_api.register_movement_from_api(
        product_id=1,
        warehouse_id=1,
        movement_type="IN",
        quantity=5,
        notes="Test"
    )

    assert result["movement_id"] == 25


def test_insufficient_stock_http_error(monkeypatch):

    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            409,
            json={
                "detail": "Insufficient stock."
            }
        )
    )

    real_client = httpx.Client

    monkeypatch.setattr(
        movements_api.httpx,
        "Client",
        lambda **kwargs: real_client(
            transport=transport,
            **kwargs
        )
    )

    with pytest.raises(
        movements_api.MovementAPIError,
        match="HTTP 409"
    ):
        movements_api.register_movement_from_api(
            product_id=1,
            warehouse_id=1,
            movement_type="OUT",
            quantity=100
        )
