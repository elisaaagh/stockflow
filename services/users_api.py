
from services.api_client import (
    api_request,
    APIClientError
)
from services.session import get_access_token


UserAPIError = APIClientError


def get_users_from_api():
    """Retrieve users from FastAPI."""

    return api_request(
        "GET",
        "/api/users",
        token=get_access_token()
    )


def create_user_from_api(
    username: str,
    password: str,
    role: str = "viewer"
):
    """Create a user through FastAPI."""

    return api_request(
        "POST",
        "/api/users",
        token=get_access_token(),
        json_data={
            "username": username,
            "password": password,
            "role": role
        }
    )
