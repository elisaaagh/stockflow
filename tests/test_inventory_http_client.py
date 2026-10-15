
from services import inventory_api


def test_get_inventory_http(monkeypatch):
    calls = []

    def fake_request(method, endpoint, **kwargs):
        calls.append({
            "method": method,
            "endpoint": endpoint,
            **kwargs
        })

        return [{
            "product_id": 1,
            "warehouse_id": 2,
            "quantity": "10.00"
        }]

    monkeypatch.setattr(
        inventory_api,
        "get_access_token",
        lambda: "test-token"
    )

    monkeypatch.setattr(
        inventory_api,
        "api_request",
        fake_request
    )

    result = inventory_api.get_inventory_from_api(
        warehouse_id=2
    )

    assert len(result) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["endpoint"] == "/api/inventory"
    assert calls[0]["token"] == "test-token"
    assert calls[0]["params"] == {"warehouse_id": 2}
