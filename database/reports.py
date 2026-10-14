
from datetime import timedelta

from psycopg.rows import dict_row

from database.db import get_connection


def get_movement_report(
    start_date,
    end_date,
    warehouse_id=None,
    product_id=None,
    movement_type=None
):
    """Retrieve movements using optional report filters."""

    if start_date > end_date:
        raise ValueError("Start date must be before end date.")

    allowed_types = (None, "IN", "OUT")

    if movement_type not in allowed_types:
        raise ValueError("Invalid movement type.")

    # Exclusive upper bound includes the complete end date.
    end_exclusive = end_date + timedelta(days=1)

    query = """
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
        WHERE sm.created_at >= %s
          AND sm.created_at < %s
    """

    params = [start_date, end_exclusive]

    if warehouse_id is not None:
        query += " AND sm.warehouse_id = %s"
        params.append(warehouse_id)

    if product_id is not None:
        query += " AND sm.product_id = %s"
        params.append(product_id)

    if movement_type is not None:
        query += " AND sm.movement_type = %s"
        params.append(movement_type)

    query += """
        ORDER BY sm.created_at DESC, sm.movement_id DESC
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
