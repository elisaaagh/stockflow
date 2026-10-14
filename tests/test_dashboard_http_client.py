
import httpx
import pytest

from services import dashboard_api


def test_dashboard_metrics_http(monkeypatch):
    def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/api/dashboard/metrics"

        return httpx.Response(
            200,
            json={
                "active_products": 12,
                "active_warehouses": 3,
                "total_movements": 50,
                "low_stock_alerts": 2
            }
        )

    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    monkeypatch.setattr(
        dashboard_api.httpx,
        "Client",
        lambda **kwargs: original_client(
            transport=transport,
            **kwargs
        )
    )

    result = dashboard_api.get_dashboard_metrics_from_api()

    assert result["active_products"] == 12
    assert result["low_stock_alerts"] == 2


def test_dashboard_activity_http(monkeypatch):
    def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/api/dashboard/activity"

        return httpx.Response(
            200,
            json=[
                {
                    "movement_date": "2026-10-14",
                    "entries": 5,
                    "exits": 3
                }
            ]
        )

    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    monkeypatch.setattr(
        dashboard_api.httpx,
        "Client",
        lambda **kwargs: original_client(
            transport=transport,
            **kwargs
        )
    )

    result = dashboard_api.get_daily_activity_from_api()

    assert len(result) == 1
    assert result[0]["entries"] == 5


def test_dashboard_http_error(monkeypatch):
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            500,
            json={"detail": "Server error"}
        )
    )

    original_client = httpx.Client

    monkeypatch.setattr(
        dashboard_api.httpx,
        "Client",
        lambda **kwargs: original_client(
            transport=transport,
            **kwargs
        )
    )

    with pytest.raises(
        dashboard_api.DashboardAPIError,
        match="HTTP 500"
    ):
        dashboard_api.get_dashboard_metrics_from_api()
