
from psycopg.rows import dict_row
from database.db import get_connection


# ==========================================
# READ - GET ALL PRODUCTS
# ==========================================

def get_all_products():
    """Retrieve all products from PostgreSQL."""

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                SELECT
                    product_id,
                    sku,
                    name,
                    description,
                    unit,
                    min_stock,
                    is_active
                FROM products
                ORDER BY name;
            """)

            return cursor.fetchall()


# ==========================================
# CREATE - REGISTER NEW PRODUCT
# ==========================================

def create_product(sku, name, description, unit, min_stock):
    """Insert a new product into PostgreSQL."""

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO products
                    (sku, name, description, unit, min_stock)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING product_id;
                """,
                (sku, name, description, unit, min_stock)
            )

            product_id = cursor.fetchone()[0]

    return product_id


# ==========================================
# UPDATE - EDIT EXISTING PRODUCT
# ==========================================

def update_product(product_id, name, description, unit, min_stock):
    """Update an existing product in PostgreSQL."""

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE products
                SET
                    name = %s,
                    description = %s,
                    unit = %s,
                    min_stock = %s
                WHERE product_id = %s
                RETURNING product_id;
                """,
                (name, description, unit, min_stock, product_id)
            )

            result = cursor.fetchone()

    return result is not None

# ==========================================
# ACTIVATE / DEACTIVATE PRODUCT
# ==========================================

def change_product_status(product_id, is_active):
    """Activate or deactivate an existing product."""

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE products
                SET is_active = %s
                WHERE product_id = %s
                RETURNING product_id;
                """,
                (is_active, product_id)
            )

            result = cursor.fetchone()

    return result is not None
