
from psycopg.rows import dict_row

from database.db import get_connection


# ==========================================
# GET WAREHOUSES
# ==========================================

def get_warehouses():
    """Return all registered warehouses."""

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                SELECT
                    warehouse_id,
                    name,
                    location,
                    is_active
                FROM warehouses
                ORDER BY name;
            """)

            return cursor.fetchall()


# ==========================================
# GET INVENTORY
# ==========================================

def get_inventory():
    """Return stock for every product and warehouse."""

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                SELECT
                    p.product_id,
                    p.sku,
                    p.name AS product,
                    p.unit,
                    p.is_active,
                    w.warehouse_id,
                    w.name AS warehouse,
                    COALESCE(i.quantity, 0) AS quantity,
                    p.min_stock,
                    CASE
                        WHEN COALESCE(i.quantity, 0) < p.min_stock
                            THEN 'LOW'
                        WHEN COALESCE(i.quantity, 0) = p.min_stock
                            THEN 'AT MINIMUM'
                        ELSE 'OK'
                    END AS stock_status
                FROM products p
                CROSS JOIN warehouses w
                LEFT JOIN inventory i
                    ON i.product_id = p.product_id
                    AND i.warehouse_id = w.warehouse_id
                ORDER BY w.name, p.name;
            """)

            return cursor.fetchall()


# ==========================================
# GET LOW STOCK
# ==========================================

def get_low_stock():
    """Return stock below the minimum threshold."""

    inventory = get_inventory()

    return [
        item
        for item in inventory
        if item["stock_status"] == "LOW"
        and item["is_active"]
    ]
