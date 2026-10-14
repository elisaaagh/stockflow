
import os

import httpx
from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


class DashboardAPIError(Exception):
    """Error communicating with Dashboard API."""
    pass


def send_dashboard_request(endpoint):
    """Retrieve dashboard data through HTTP."""

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{API_BASE_URL}{endpoint}"
            )

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as error:
        raise DashboardAPIError(
            f"Dashboard API returned HTTP "
            f"{error.response.status_code}."
        ) from error

    except httpx.RequestError as error:
        raise DashboardAPIError(
            "Cannot connect to StockFlow API. "
            "Verify that FastAPI is running."
        ) from error


# ==========================================
# DASHBOARD METRICS
# ==========================================

def get_dashboard_metrics_from_api():
    return send_dashboard_request(
        "/api/dashboard/metrics"
    )


# ==========================================
# DAILY ACTIVITY
# ==========================================

def get_daily_activity_from_api():
    return send_dashboard_request(
        "/api/dashboard/activity"
    )
