
import pytest

from services import dashboard_api
from services.api_client import APIClientError


# ==========================================
# DASHBOARD METRICS
# ==========================================

def test_dashboard_metrics_http(monkeypatch):
    calls = []

    def fake_request(method, endpoint, **kwargs):
        calls.append({
            "method": method,
            "endpoint": endpoint,
            **kwargs
        })

        return {
            "total_products": 10,
            "total_warehouses": 3,
            "low_stock_products": 2
        }

    monkeypatch.setattr(
        dashboard_api,
        "get_access_token",
        lambda: "test-token"
    )

    monkeypatch.setattr(
        dashboard_api,
        "api_request",
        fake_request
    )

    result = dashboard_api.get_dashboard_metrics_from_api()

    assert result["total_products"] == 10
    assert calls[0]["method"] == "GET"
    assert calls[0]["endpoint"] == "/api/dashboard/metrics"
    assert calls[0]["token"] == "test-token"


# ==========================================
# DAILY ACTIVITY
# ==========================================

def test_dashboard_activity_http(monkeypatch):
    calls = []

    def fake_request(method, endpoint, **kwargs):
        calls.append({
            "method": method,
            "endpoint": endpoint,
            **kwargs
        })

        return [
            {
                "date": "2026-10-15",
                "total_movements": 5
            }
        ]

    monkeypatch.setattr(
        dashboard_api,
        "get_access_token",
        lambda: "test-token"
    )

    monkeypatch.setattr(
        dashboard_api,
        "api_request",
        fake_request
    )

    result = dashboard_api.get_daily_activity_from_api()

    assert len(result) == 1
    assert result[0]["total_movements"] == 5
    assert calls[0]["method"] == "GET"
    assert calls[0]["endpoint"] == "/api/dashboard/activity"
    assert calls[0]["token"] == "test-token"


# ==========================================
# HTTP ERROR HANDLING
# ==========================================

def test_dashboard_http_error(monkeypatch):

    def fake_request(method, endpoint, **kwargs):
        raise APIClientError(
            "Cannot connect to StockFlow API.",
            status_code=503
        )

    monkeypatch.setattr(
        dashboard_api,
        "get_access_token",
        lambda: "test-token"
    )

    monkeypatch.setattr(
        dashboard_api,
        "api_request",
        fake_request
    )

    with pytest.raises(APIClientError) as error:
        dashboard_api.get_dashboard_metrics_from_api()

    assert error.value.status_code == 503
    assert "Cannot connect" in str(error.value)
