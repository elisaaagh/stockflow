
from datetime import datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from api.main import app
import api.routers.reports as reports_router


client = TestClient(app)


SAMPLE_REPORT = [{
    "movement_id": 1,
    "created_at": datetime(2026, 10, 14, 12, 0),
    "sku": "TEST001",
    "product": "Test Product",
    "warehouse": "Main Warehouse",
    "movement_type": "IN",
    "quantity": Decimal("5.00"),
    "unit": "Pieza",
    "notes": "Test entry"
}]


def test_get_movement_report(monkeypatch):
    def fake_report(**kwargs):
        assert kwargs["start_date"].isoformat() == "2026-10-01"
        assert kwargs["end_date"].isoformat() == "2026-10-15"
        return SAMPLE_REPORT

    monkeypatch.setattr(
        reports_router,
        "get_movement_report",
        fake_report
    )

    response = client.get(
        "/api/reports/movements",
        params={
            "start_date": "2026-10-01",
            "end_date": "2026-10-15"
        }
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["sku"] == "TEST001"


def test_report_filters(monkeypatch):
    def fake_report(**kwargs):
        assert kwargs["warehouse_id"] == 2
        assert kwargs["product_id"] == 1
        assert kwargs["movement_type"] == "OUT"
        return []

    monkeypatch.setattr(
        reports_router,
        "get_movement_report",
        fake_report
    )

    response = client.get(
        "/api/reports/movements",
        params={
            "start_date": "2026-10-01",
            "end_date": "2026-10-15",
            "warehouse_id": 2,
            "product_id": 1,
            "movement_type": "OUT"
        }
    )

    assert response.status_code == 200
    assert response.json() == []


def test_invalid_date_range():
    response = client.get(
        "/api/reports/movements",
        params={
            "start_date": "2026-10-15",
            "end_date": "2026-10-01"
        }
    )

    assert response.status_code == 422


def test_invalid_movement_type():
    response = client.get(
        "/api/reports/movements",
        params={
            "start_date": "2026-10-01",
            "end_date": "2026-10-15",
            "movement_type": "TRANSFER"
        }
    )

    assert response.status_code == 422


def test_invalid_warehouse_id():
    response = client.get(
        "/api/reports/movements",
        params={
            "start_date": "2026-10-01",
            "end_date": "2026-10-15",
            "warehouse_id": -1
        }
    )

    assert response.status_code == 422
