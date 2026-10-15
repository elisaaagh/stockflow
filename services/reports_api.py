
from datetime import date

from services.api_client import (
    api_request,
    APIClientError as ReportsAPIError
)
from services.session import get_access_token


def get_movement_report_from_api(
    start_date: date,
    end_date: date,
    warehouse_id=None,
    product_id=None,
    movement_type=None
):
    if start_date > end_date:
        raise ValueError(
            "Start date must be before end date."
        )

    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }

    if warehouse_id is not None:
        params["warehouse_id"] = warehouse_id

    if product_id is not None:
        params["product_id"] = product_id

    if movement_type is not None:
        params["movement_type"] = movement_type

    return api_request(
        "GET",
        "/api/reports/movements",
        token=get_access_token(),
        params=params
    )
