
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from api.dependencies.auth import get_current_user
from api.security import (
    create_access_token,
    verify_password
)
from database.users import get_user_by_username


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    user_id: int
    username: str
    role: str
    is_active: bool


@router.post("/login", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends()
):
    username = form.username.strip().lower()

    user = get_user_by_username(username)

    # Constant-time comparison against a dummy hash
    # is useful when the username does not exist.
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    valid_password = verify_password(
        form.password,
        user["password_hash"]
    )

    if not valid_password or not user["is_active"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token(
        user_id=user["user_id"]
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get(
    "/me",
    response_model=CurrentUserResponse
)
def read_current_user(
    current_user: dict = Depends(get_current_user)
):
    return current_user
