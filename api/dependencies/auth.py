
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from api.security import decode_access_token
from database.users import get_user_by_id


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    """Authenticate the current user."""

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        user_id = decode_access_token(token)
    except ValueError:
        raise credentials_error

    user = get_user_by_id(user_id)

    if user is None or not user["is_active"]:
        raise credentials_error

    return user

def require_roles(*allowed_roles: str):
    """Allow access only to specified roles."""

    def check_role(
        current_user: dict = Depends(get_current_user)
    ):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions."
            )

        return current_user

    return check_role


# Reusable role dependencies
require_admin = require_roles("admin")
require_operator = require_roles("admin", "operator")
require_viewer = require_roles(
    "admin", "operator", "viewer"
)
