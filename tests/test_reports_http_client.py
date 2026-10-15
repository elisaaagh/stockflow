
from datetime import date

import httpx
import pytest

from services import reports_api


def test_get_report_with_filters(monkeypatch):
    def mock_response(request):
        assert request.method == "GET"
        assert request.url.path == "/api/reports/movements"

        params = request.url.params

        assert params["start_date"] == "2026-10-01"
        assert params["end_date"] == "2026-10-15"
        assert params["warehouse_id"] == "2"
        assert params["product_id"] == "1"
        assert params["movement_type"] == "OUT"

        return httpx.Response(
            200,
            json=[{
                "movement_id": 10,
                "movement_type": "OUT",
                "quantity": "5.00"
            }]
        )

    transport = httpx.MockTransport(mock_response)
    original_client = httpx.Client

    monkeypatch.setattr(
        reports_api.httpx,
        "Client",
        lambda **kwargs: original_client(
            transport=transport,
            **kwargs
        )
    )

    result = reports_api.get_movement_report_from_api(
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 15),
        warehouse_id=2,
        product_id=1,
        movement_type="OUT"
    )

    assert len(result) == 1
    assert result[0]["movement_type"] == "OUT"


def test_report_invalid_date_range():
    with pytest.raises(ValueError):
        reports_api.get_movement_report_from_api(
            start_date=date(2026, 10, 15),
            end_date=date(2026, 10, 1)
        )


def test_report_http_error(monkeypatch):
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            422,
            json={"detail": "Invalid date range"}
        )
    )

    original_client = httpx.Client

    monkeypatch.setattr(
        reports_api.httpx,
        "Client",
        lambda **kwargs: original_client(
            transport=transport,
            **kwargs
        )
    )

    with pytest.raises(
        reports_api.ReportsAPIError,
        match="HTTP 422"
    ):
        reports_api.get_movement_report_from_api(
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 15)
        )
