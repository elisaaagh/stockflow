
from decimal import Decimal, InvalidOperation

from psycopg.rows import dict_row

from database.db import get_connection


# ==========================================
# BUSINESS VALIDATION ERROR
# ==========================================

class StockMovementError(Exception):
    """Error caused by an invalid inventory operation."""
    pass


# ==========================================
# REGISTER STOCK MOVEMENT
# ==========================================

def register_movement(
    product_id,
    warehouse_id,
    movement_type,
    quantity,
    notes=""
):
    """Register a stock entry or exit atomically."""

    if movement_type not in ("IN", "OUT"):
        raise StockMovementError(
            "Movement type must be IN or OUT."
        )

    try:
        quantity = Decimal(str(quantity))
    except (InvalidOperation, ValueError):
        raise StockMovementError("Invalid quantity.")

    if (
        not quantity.is_finite()
        or quantity <= 0
        or quantity.as_tuple().exponent < -2
        or quantity >= Decimal("10000000000")
    ):
        raise StockMovementError(
            "Quantity must be positive with up to 2 decimals."
        )

    with get_connection() as conn:
        with conn.cursor() as cursor:

            # Lock the product row to serialize movements.
            cursor.execute(
                """
                SELECT is_active
                FROM products
                WHERE product_id = %s
                FOR UPDATE;
                """,
                (product_id,)
            )

            product = cursor.fetchone()

            if product is None:
                raise StockMovementError(
                    "Product not found."
                )

            if not product[0]:
                raise StockMovementError(
                    "Inactive products cannot be moved."
                )

            # Validate warehouse and lock its row.
            cursor.execute(
                """
                SELECT is_active
                FROM warehouses
                WHERE warehouse_id = %s
                FOR UPDATE;
                """,
                (warehouse_id,)
            )

            warehouse = cursor.fetchone()

            if warehouse is None:
                raise StockMovementError(
                    "Warehouse not found."
                )

            if not warehouse[0]:
                raise StockMovementError(
                    "Warehouse is inactive."
                )

            # Create a zero-stock row if missing.
            cursor.execute(
                """
                INSERT INTO inventory (
                    product_id,
                    warehouse_id,
                    quantity
                )
                VALUES (%s, %s, 0)
                ON CONFLICT (product_id, warehouse_id)
                DO NOTHING;
                """,
                (product_id, warehouse_id)
            )

            # Lock the inventory record.
            cursor.execute(
                """
                SELECT quantity
                FROM inventory
                WHERE product_id = %s
                  AND warehouse_id = %s
                FOR UPDATE;
                """,
                (product_id, warehouse_id)
            )

            current_stock = cursor.fetchone()[0]

            if movement_type == "IN":
                new_stock = current_stock + quantity
            else:
                if quantity > current_stock:
                    raise StockMovementError(
                        f"Insufficient stock. "
                        f"Available: {current_stock}"
                    )

                new_stock = current_stock - quantity

            # Update inventory.
            cursor.execute(
                """
                UPDATE inventory
                SET quantity = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE product_id = %s
                  AND warehouse_id = %s;
                """,
                (new_stock, product_id, warehouse_id)
            )

            # Insert movement history.
            cursor.execute(
                """
                INSERT INTO stock_movements (
                    product_id,
                    warehouse_id,
                    movement_type,
                    quantity,
                    notes
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING movement_id;
                """,
                (
                    product_id,
                    warehouse_id,
                    movement_type,
                    quantity,
                    notes
                )
            )

            movement_id = cursor.fetchone()[0]

    return movement_id


# ==========================================
# MOVEMENT HISTORY
# ==========================================

def get_movements():
    """Return movement history, newest first."""

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                SELECT
                    sm.movement_id,
                    sm.created_at,
                    p.sku,
                    p.name AS product,
                    w.name AS warehouse,
                    sm.movement_type,
                    sm.quantity,
                    p.unit,
                    sm.notes
                FROM stock_movements sm
                JOIN products p
                    ON sm.product_id = p.product_id
                JOIN warehouses w
                    ON sm.warehouse_id = w.warehouse_id
                ORDER BY
                    sm.created_at DESC,
                    sm.movement_id DESC;
            """)

            return cursor.fetchall()
