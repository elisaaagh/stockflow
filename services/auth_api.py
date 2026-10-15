
import os

import httpx
from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


class AuthenticationError(Exception):
    """Error during authentication."""
    pass


def login_user(username: str, password: str):
    """Authenticate a user with FastAPI."""

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{API_BASE_URL}/api/auth/login",
                data={
                    "username": username,
                    "password": password
                }
            )

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as error:
        if error.response.status_code == 401:
            raise AuthenticationError(
                "Invalid username or password."
            ) from error

        raise AuthenticationError(
            "Authentication service returned an error."
        ) from error

    except httpx.RequestError as error:
        raise AuthenticationError(
            "Cannot connect to StockFlow API."
        ) from error


def get_authenticated_user(access_token: str):
    """Retrieve the current user's public profile."""

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{API_BASE_URL}/api/auth/me",
                headers={
                    "Authorization": f"Bearer {access_token}"
                }
            )

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as error:
        if error.response.status_code == 401:
            raise AuthenticationError(
                "Your session is invalid or has expired."
            ) from error

        raise AuthenticationError(
            "Unable to verify your account."
        ) from error

    except httpx.RequestError as error:
        raise AuthenticationError(
            "Cannot connect to StockFlow API."
        ) from error
