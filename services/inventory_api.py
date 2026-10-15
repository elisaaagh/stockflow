
from services.api_client import (
    api_request,
    APIClientError as InventoryAPIError
)
from services.session import get_access_token


def get_warehouses_from_api():
    return api_request(
        "GET",
        "/api/warehouses",
        token=get_access_token()
    )


def get_inventory_from_api(warehouse_id=None):
    params = {}

    if warehouse_id is not None:
        params["warehouse_id"] = warehouse_id

    return api_request(
        "GET",
        "/api/inventory",
        token=get_access_token(),
        params=params
    )


def get_low_stock_from_api():
    return api_request(
        "GET",
        "/api/inventory/low-stock",
        token=get_access_token()
    )
