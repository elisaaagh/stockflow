
from services.api_client import api_request
from services.session import get_access_token


def get_products_from_api():
    return api_request(
        "GET",
        "/api/products",
        token=get_access_token()
    )


def create_product_from_api(
    sku, name, description, unit, min_stock
):
    return api_request(
        "POST",
        "/api/products",
        token=get_access_token(),
        json_data={
            "sku": sku,
            "name": name,
            "description": description,
            "unit": unit,
            "min_stock": str(min_stock)
        }
    )


def update_product_from_api(
    product_id, name, description, unit, min_stock
):
    return api_request(
        "PUT",
        f"/api/products/{product_id}",
        token=get_access_token(),
        json_data={
            "name": name,
            "description": description,
            "unit": unit,
            "min_stock": str(min_stock)
        }
    )


def change_product_status_from_api(
    product_id, is_active
):
    return api_request(
        "PATCH",
        f"/api/products/{product_id}/status",
        token=get_access_token(),
        json_data={"is_active": is_active}
    )

from services.api_client import APIClientError as ProductAPIError