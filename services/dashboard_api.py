
from services.api_client import (
    api_request,
    APIClientError as DashboardAPIError
)
from services.session import get_access_token


def get_dashboard_metrics_from_api():
    return api_request(
        "GET",
        "/api/dashboard/metrics",
        token=get_access_token()
    )


def get_daily_activity_from_api():
    return api_request(
        "GET",
        "/api/dashboard/activity",
        token=get_access_token()
    )
