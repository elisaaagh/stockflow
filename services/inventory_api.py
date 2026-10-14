
import os

import httpx
from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


class InventoryAPIError(Exception):
    """Error while communicating with Inventory API."""
    pass


def send_inventory_request(endpoint, params=None):
    """Send a GET request to StockFlow API."""

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{API_BASE_URL}{endpoint}",
                params=params
            )

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as error:
        raise InventoryAPIError(
            f"Inventory API returned HTTP "
            f"{error.response.status_code}."
        ) from error

    except httpx.RequestError as error:
        raise InventoryAPIError(
            "Cannot connect to StockFlow API. "
            "Verify that FastAPI is running."
        ) from error


# ==========================================
# WAREHOUSES
# ==========================================

def get_warehouses_from_api():
    return send_inventory_request("/api/warehouses")


# ==========================================
# INVENTORY
# ==========================================

def get_inventory_from_api(warehouse_id=None):
    params = {}

    if warehouse_id is not None:
        params["warehouse_id"] = warehouse_id

    return send_inventory_request(
        "/api/inventory",
        params=params
    )


# ==========================================
# LOW STOCK
# ==========================================

def get_low_stock_from_api():
    return send_inventory_request(
        "/api/inventory/low-stock"
    )
