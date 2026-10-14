
from psycopg.rows import dict_row

from database.db import get_connection


# ==========================================
# DASHBOARD METRICS
# ==========================================

def get_dashboard_metrics():

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            cursor.execute("""
                SELECT
                    (SELECT COUNT(*)
                     FROM products
                     WHERE is_active = TRUE)
                     AS active_products,

                    (SELECT COUNT(*)
                     FROM warehouses
                     WHERE is_active = TRUE)
                     AS active_warehouses,

                    (SELECT COUNT(*)
                     FROM stock_movements)
                     AS total_movements;
            """)

            metrics = cursor.fetchone()

            cursor.execute("""
                SELECT COUNT(*) AS low_stock_alerts
                FROM products p
                CROSS JOIN warehouses w
                LEFT JOIN inventory i
                    ON i.product_id = p.product_id
                    AND i.warehouse_id = w.warehouse_id
                WHERE p.is_active = TRUE
                  AND w.is_active = TRUE
                  AND COALESCE(i.quantity, 0) < p.min_stock;
            """)

            metrics["low_stock_alerts"] = (
                cursor.fetchone()["low_stock_alerts"]
            )

            return metrics


# ==========================================
# DAILY MOVEMENT ACTIVITY
# ==========================================

def get_daily_activity():

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            cursor.execute("""
                SELECT
                    created_at::date AS movement_date,

                    COUNT(*) FILTER (
                        WHERE movement_type = 'IN'
                    ) AS entries,

                    COUNT(*) FILTER (
                        WHERE movement_type = 'OUT'
                    ) AS exits

                FROM stock_movements

                WHERE created_at >=
                    CURRENT_DATE - INTERVAL '6 days'

                GROUP BY created_at::date
                ORDER BY movement_date;
            """)

            return cursor.fetchall()
