
import httpx
import pytest

from services import inventory_api


def test_get_inventory_from_api(monkeypatch):

    def mock_response(request):
        assert request.method == "GET"
        assert request.url.path == "/api/inventory"

        return httpx.Response(
            200,
            json=[
                {
                    "product_id": 1,
                    "warehouse_id": 1,
                    "quantity": 10
                }
            ]
        )

    transport = httpx.MockTransport(mock_response)

    real_client = httpx.Client

    monkeypatch.setattr(
        inventory_api.httpx,
        "Client",
        lambda **kwargs: real_client(
            transport=transport,
            **kwargs
        )
    )

    result = inventory_api.get_inventory_from_api()

    assert len(result) == 1
    assert result[0]["quantity"] == 10


def test_inventory_api_http_error(monkeypatch):

    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            500,
            json={"detail": "Internal Server Error"}
        )
    )

    real_client = httpx.Client

    monkeypatch.setattr(
        inventory_api.httpx,
        "Client",
        lambda **kwargs: real_client(
            transport=transport,
            **kwargs
        )
    )

    with pytest.raises(
        inventory_api.InventoryAPIError,
        match="HTTP 500"
    ):
        inventory_api.get_warehouses_from_api()
