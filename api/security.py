
from pwdlib import PasswordHash

import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from jwt.exceptions import InvalidTokenError


load_dotenv()


def get_jwt_settings():
    """Load JWT settings without unsafe defaults."""

    secret = os.getenv("JWT_SECRET_KEY")

    if not secret or len(secret) < 32:
        raise RuntimeError(
            "JWT_SECRET_KEY must contain at least 32 characters."
        )

    algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    if algorithm != "HS256":
        raise RuntimeError("Unsupported JWT algorithm.")

    expire_minutes = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    if not 1 <= expire_minutes <= 1440:
        raise RuntimeError("Invalid token expiration.")

    return secret, algorithm, expire_minutes


def create_access_token(user_id: int) -> str:
    """Create a signed access token."""

    secret, algorithm, expire_minutes = get_jwt_settings()

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=expire_minutes),
        "type": "access"
    }

    return jwt.encode(
        payload,
        secret,
        algorithm=algorithm
    )


def decode_access_token(token: str) -> int:
    """Validate a token and return the user's ID."""

    secret, algorithm, _ = get_jwt_settings()

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[algorithm],
            options={"require": ["sub", "iat", "nbf", "exp"]}
        )

        if payload.get("type") != "access":
            raise ValueError("Invalid token type.")

        user_id = int(payload["sub"])

        if user_id <= 0:
            raise ValueError("Invalid user ID.")

        return user_id

    except (InvalidTokenError, ValueError, TypeError) as error:
        raise ValueError("Invalid or expired access token.") from error


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Generate a secure password hash."""

    if not isinstance(password, str) or len(password) < 12:
        raise ValueError(
            "Password must contain at least 12 characters."
        )

    if len(password.encode("utf-8")) > 1024:
        raise ValueError("Password is too long.")

    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Verify a password against its stored hash."""

    return password_hasher.verify(
        plain_password,
        hashed_password
    )

