
from fastapi import APIRouter, Depends, HTTPException, status
from psycopg.errors import UniqueViolation

from api.dependencies.auth import require_admin
from api.schemas import (
    UserCreate,
    UserResponse,
    UserCreatedResponse
)
from api.security import hash_password
from database.users import (
    get_all_users,
    get_user_by_id,
    create_user
)


router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
    dependencies=[Depends(require_admin)]
)


# ==========================================
# GET ALL USERS
# ==========================================

@router.get("", response_model=list[UserResponse])
def list_users():
    return get_all_users()


# ==========================================
# CREATE USER
# ==========================================

@router.post(
    "",
    response_model=UserCreatedResponse,
    status_code=status.HTTP_201_CREATED
)
def add_user(payload: UserCreate):

    password_hash = hash_password(payload.password)

    try:
        user_id = create_user(
            username=payload.username,
            password_hash=password_hash,
            role=payload.role
        )

    except UniqueViolation as error:
        raise HTTPException(
            status_code=409,
            detail="Username already exists."
        ) from error

    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve created user."
        )

    return user
