
import httpx
import pytest

from services import api_client


def test_authenticated_get(monkeypatch):
    def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/api/products"
        assert (
            request.headers["Authorization"]
            == "Bearer test-token"
        )

        return httpx.Response(
            200,
            json=[{"product_id": 1, "sku": "TEST001"}]
        )

    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    monkeypatch.setattr(
        api_client.httpx,
        "Client",
        lambda **kwargs: original_client(
            transport=transport,
            **kwargs
        )
    )

    result = api_client.api_request(
        "GET",
        "/api/products",
        token="test-token"
    )

    assert result[0]["sku"] == "TEST001"


def test_missing_token():
    with pytest.raises(
        api_client.APIClientError
    ) as error:
        api_client.api_request(
            "GET",
            "/api/products",
            token=""
        )

    assert error.value.status_code == 401


def test_insufficient_permissions(monkeypatch):
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            403,
            json={"detail": "Insufficient permissions."}
        )
    )

    original_client = httpx.Client

    monkeypatch.setattr(
        api_client.httpx,
        "Client",
        lambda **kwargs: original_client(
            transport=transport,
            **kwargs
        )
    )

    with pytest.raises(
        api_client.APIClientError
    ) as error:
        api_client.api_request(
            "POST",
            "/api/movements",
            token="test-token",
            json_data={"quantity": "5.00"}
        )

    assert error.value.status_code == 403
