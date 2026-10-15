
from services.api_client import (
    api_request,
    APIClientError as MovementAPIError
)
from services.session import get_access_token


def get_movements_from_api():
    return api_request(
        "GET",
        "/api/movements",
        token=get_access_token()
    )


def register_movement_from_api(
    product_id,
    warehouse_id,
    movement_type,
    quantity,
    notes=""
):
    return api_request(
        "POST",
        "/api/movements",
        token=get_access_token(),
        json_data={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "movement_type": movement_type,
            "quantity": str(quantity),
            "notes": notes
        }
    )
