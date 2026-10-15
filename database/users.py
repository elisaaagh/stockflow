
from psycopg.rows import dict_row

from database.db import get_connection


# ==========================================
# FIND USER BY USERNAME
# ==========================================

def get_user_by_username(username):
    """Retrieve a user for authentication."""

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    user_id,
                    username,
                    password_hash,
                    role,
                    is_active
                FROM users
                WHERE username = %s;
                """,
                (username,)
            )

            return cursor.fetchone()


# ==========================================
# FIND USER BY ID
# ==========================================

def get_user_by_id(user_id):
    """Retrieve a user by primary key."""

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    user_id,
                    username,
                    password_hash,
                    role,
                    is_active
                FROM users
                WHERE user_id = %s;
                """,
                (user_id,)
            )

            return cursor.fetchone()


# ==========================================
# CREATE USER
# ==========================================

def create_user(username, password_hash, role="viewer"):
    """Store a new user with a precomputed password hash."""

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (
                    username,
                    password_hash,
                    role
                )
                VALUES (%s, %s, %s)
                RETURNING user_id;
                """,
                (username, password_hash, role)
            )

            return cursor.fetchone()[0]
