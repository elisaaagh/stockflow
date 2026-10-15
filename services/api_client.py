
import os

import httpx
from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


class APIClientError(Exception):
    """General API communication error."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


def api_request(
    method: str,
    endpoint: str,
    *,
    token: str,
    params=None,
    json_data=None
):
    """Send an authenticated request to FastAPI."""

    if not token:
        raise APIClientError(
            "Authentication is required.",
            status_code=401
        )

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.request(
                method=method,
                url=f"{API_BASE_URL}{endpoint}",
                headers={
                    "Authorization": f"Bearer {token}"
                },
                params=params,
                json=json_data
            )

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code

        if status_code == 401:
            message = "Session expired or invalid."
        elif status_code == 403:
            message = "You do not have permission for this action."
        else:
            try:
                detail = error.response.json().get(
                    "detail", "Request failed."
                )
                message = (
                    detail if isinstance(detail, str)
                    else "Request validation failed."
                )
            except (ValueError, AttributeError):
                message = "Request failed."

        raise APIClientError(
            message,
            status_code=status_code
        ) from error

    except httpx.RequestError as error:
        raise APIClientError(
            "Cannot connect to StockFlow API."
        ) from error
