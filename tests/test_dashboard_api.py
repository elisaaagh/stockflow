
from datetime import date

from fastapi.testclient import TestClient

from api.main import app
import api.routers.dashboard as dashboard_router
from tests.auth_helpers import authenticated_as

client = TestClient(app)


def test_dashboard_metrics(monkeypatch):

    monkeypatch.setattr(
        dashboard_router,
        "get_dashboard_metrics",
        lambda: {
            "active_products": 15,
            "active_warehouses": 3,
            "total_movements": 40,
            "low_stock_alerts": 5
        }
    )

    with authenticated_as("viewer"):
        response = client.get("/api/dashboard/metrics")

    assert response.status_code == 200
    assert response.json()["active_products"] == 15
    assert response.json()["low_stock_alerts"] == 5


def test_dashboard_activity(monkeypatch, login_as):
    login_as("viewer")

    monkeypatch.setattr(
        dashboard_router,
        "get_daily_activity",
        lambda: [
            {
                "movement_date": date(2026, 10, 14),
                "entries": 6,
                "exits": 4
            }
        ]
    )

    response = client.get("/api/dashboard/activity")

    assert response.status_code == 200
    assert response.json()[0]["movement_date"] == "2026-10-14"
    assert response.json()[0]["entries"] == 6
    assert response.json()[0]["exits"] == 4
