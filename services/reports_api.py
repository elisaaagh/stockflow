
import os
from datetime import date

import httpx
from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


class ReportsAPIError(Exception):
    """Error while communicating with Reports API."""
    pass


def get_movement_report_from_api(
    start_date: date,
    end_date: date,
    warehouse_id=None,
    product_id=None,
    movement_type=None
):
    """Retrieve filtered movements from FastAPI."""

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

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.get(
                f"{API_BASE_URL}/api/reports/movements",
                params=params
            )

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code

        try:
            detail = error.response.json().get(
                "detail",
                "Unable to generate report."
            )
        except (ValueError, AttributeError):
            detail = "Unable to generate report."

        if isinstance(detail, (list, dict)):
            detail = str(detail)

        raise ReportsAPIError(
            f"HTTP {status_code}: {detail}"
        ) from error

    except httpx.RequestError as error:
        raise ReportsAPIError(
            "Cannot connect to StockFlow API. "
            "Verify that FastAPI is running."
        ) from error
