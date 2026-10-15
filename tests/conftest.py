
import os
from pathlib import Path

import psycopg
import pytest
from dotenv import dotenv_values

import database.movements as movements
from api.main import app
from api.dependencies.auth import get_current_user

TEST_ENV = Path(__file__).resolve().parents[1] / ".env.test"


@pytest.fixture
def test_db(monkeypatch):

    config = dotenv_values(TEST_ENV)

    # Never allow tests to use the main database.
    db_name = config.get("DB_TEST_NAME")

    if db_name != "stockflow_test_db":
        pytest.fail(
            "Tests must use stockflow_test_db."
        )

    def connect_test_db():
        return psycopg.connect(
            host=config.get("DB_TEST_HOST"),
            port=config.get("DB_TEST_PORT"),
            dbname=db_name,
            user=config.get("DB_TEST_USER"),
            password=config.get("DB_TEST_PASSWORD")
        )

    # Redirect movement operations to test database.
    monkeypatch.setattr(
        movements,
        "get_connection",
        connect_test_db
    )

    # Reset test data before each test.
    with connect_test_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                TRUNCATE TABLE
                    stock_movements,
                    inventory,
                    products,
                    warehouses
                RESTART IDENTITY CASCADE;
            """)

    yield connect_test_db


@pytest.fixture
def login_as():
    """Simulate an authenticated user for one test."""

    previous = app.dependency_overrides.get(
        get_current_user
    )

    def _login(role="admin"):
        app.dependency_overrides[get_current_user] = (
            lambda: {
                "user_id": 1,
                "username": "testuser",
                "role": role,
                "is_active": True
            }
        )

    try:
        yield _login
    finally:
        if previous is None:
            app.dependency_overrides.pop(
                get_current_user,
                None
            )
        else:
            app.dependency_overrides[get_current_user] = previous
