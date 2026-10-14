
import os

import httpx
from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


class MovementAPIError(Exception):
    """Error communicating with Movements API."""
    pass


def send_movement_request(method, endpoint, payload=None):
    """Send an HTTP request to the Movements API."""

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.request(
                method=method,
                url=f"{API_BASE_URL}{endpoint}",
                json=payload
            )

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code

        try:
            detail = error.response.json().get(
                "detail",
                "Request failed."
            )
        except (ValueError, AttributeError):
            detail = "Request failed."

        if isinstance(detail, (list, dict)):
            detail = str(detail)

        raise MovementAPIError(
            f"HTTP {status_code}: {detail}"
        ) from error

    except httpx.RequestError as error:
        raise MovementAPIError(
            "Cannot connect to StockFlow API. "
            "Verify that FastAPI is running."
        ) from error


# ==========================================
# GET MOVEMENT HISTORY
# ==========================================

def get_movements_from_api():
    return send_movement_request(
        "GET",
        "/api/movements"
    )


# ==========================================
# REGISTER STOCK MOVEMENT
# ==========================================

def register_movement_from_api(
    product_id,
    warehouse_id,
    movement_type,
    quantity,
    notes=""
):
    payload = {
        "product_id": product_id,
        "warehouse_id": warehouse_id,
        "movement_type": movement_type,
        "quantity": str(quantity),
        "notes": notes
    }

    return send_movement_request(
        "POST",
        "/api/movements",
        payload=payload
    )
