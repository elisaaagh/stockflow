
from datetime import date

import pytest

from services import reports_api
from services.api_client import APIClientError


# ==========================================
# REPORT WITH FILTERS
# ==========================================

def test_get_report_with_filters(monkeypatch):
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
                "product_id": 2,
                "warehouse_id": 3,
                "movement_type": "IN",
                "quantity": "10.00"
            }
        ]

    monkeypatch.setattr(
        reports_api,
        "get_access_token",
        lambda: "test-token"
    )

    monkeypatch.setattr(
        reports_api,
        "api_request",
        fake_request
    )

    result = reports_api.get_movement_report_from_api(
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 15),
        warehouse_id=3,
        product_id=2,
        movement_type="IN"
    )

    assert len(result) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["endpoint"] == "/api/reports/movements"
    assert calls[0]["token"] == "test-token"

    assert calls[0]["params"] == {
        "start_date": "2026-10-01",
        "end_date": "2026-10-15",
        "warehouse_id": 3,
        "product_id": 2,
        "movement_type": "IN"
    }


# ==========================================
# INVALID DATE RANGE
# ==========================================

def test_report_invalid_date_range():
    with pytest.raises(ValueError):
        reports_api.get_movement_report_from_api(
            start_date=date(2026, 10, 15),
            end_date=date(2026, 10, 1)
        )


# ==========================================
# HTTP ERROR
# ==========================================

def test_report_http_error(monkeypatch):

    def fake_request(method, endpoint, **kwargs):
        raise APIClientError(
            "Cannot connect to StockFlow API.",
            status_code=503
        )

    monkeypatch.setattr(
        reports_api,
        "get_access_token",
        lambda: "test-token"
    )

    monkeypatch.setattr(
        reports_api,
        "api_request",
        fake_request
    )

    with pytest.raises(APIClientError) as error:
        reports_api.get_movement_report_from_api(
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 15)
        )

    assert error.value.status_code == 503
    assert "Cannot connect" in str(error.value)
