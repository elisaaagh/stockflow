
import pytest

from database.movements import (
    register_movement,
    StockMovementError
)


# ==========================================
# TEST DATA
# ==========================================

@pytest.fixture
def sample_inventory(test_db):
    """Create product, warehouse and initial stock."""

    with test_db() as conn:
        with conn.cursor() as cursor:

            cursor.execute("""
                INSERT INTO products
                    (sku, name, unit, min_stock)
                VALUES ('TEST001', 'Test Product', 'Pieza', 10)
                RETURNING product_id;
            """)

            product_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO warehouses (name)
                VALUES ('Test Warehouse')
                RETURNING warehouse_id;
            """)

            warehouse_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO inventory
                    (product_id, warehouse_id, quantity)
                VALUES (%s, %s, 100);
                """,
                (product_id, warehouse_id)
            )

    return product_id, warehouse_id


def read_stock(test_db, product_id, warehouse_id):
    """Read the available stock."""

    with test_db() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT quantity
                FROM inventory
                WHERE product_id = %s
                  AND warehouse_id = %s;
                """,
                (product_id, warehouse_id)
            )

            return cursor.fetchone()[0]


def count_movements(test_db):
    """Count recorded movements."""

    with test_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM stock_movements;
            """)
            return cursor.fetchone()[0]


# ==========================================
# TEST 1 - STOCK ENTRY
# ==========================================

def test_stock_entry(test_db, sample_inventory):

    product_id, warehouse_id = sample_inventory

    register_movement(
        product_id,
        warehouse_id,
        "IN",
        50,
        "Automated test"
    )

    stock = read_stock(
        test_db, product_id, warehouse_id
    )

    assert stock == 150
    assert count_movements(test_db) == 1


# ==========================================
# TEST 2 - STOCK EXIT
# ==========================================

def test_stock_exit(test_db, sample_inventory):

    product_id, warehouse_id = sample_inventory

    register_movement(
        product_id,
        warehouse_id,
        "OUT",
        30
    )

    stock = read_stock(
        test_db, product_id, warehouse_id
    )

    assert stock == 70
    assert count_movements(test_db) == 1


# ==========================================
# TEST 3 - INSUFFICIENT STOCK
# ==========================================

def test_insufficient_stock(test_db, sample_inventory):

    product_id, warehouse_id = sample_inventory

    with pytest.raises(StockMovementError):
        register_movement(
            product_id,
            warehouse_id,
            "OUT",
            200
        )

    stock = read_stock(
        test_db, product_id, warehouse_id
    )

    assert stock == 100
    assert count_movements(test_db) == 0


# ==========================================
# TEST 4 - DATABASE ROLLBACK
# ==========================================

def test_transaction_rollback(test_db, sample_inventory):

    product_id, warehouse_id = sample_inventory

    # Simulate a database failure while saving history.
    with test_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE FUNCTION reject_test_movement()
                RETURNS trigger
                LANGUAGE plpgsql
                AS $$
                BEGIN
                    RAISE EXCEPTION 'Simulated insert failure';
                END;
                $$;
            """)

            cursor.execute("""
                CREATE TRIGGER reject_movement_insert
                BEFORE INSERT ON stock_movements
                FOR EACH ROW
                EXECUTE FUNCTION reject_test_movement();
            """)

    try:
        with pytest.raises(
            Exception,
            match="Simulated insert failure"
        ):
            register_movement(
                product_id,
                warehouse_id,
                "OUT",
                30
            )

        # Inventory must remain unchanged.
        assert read_stock(
            test_db, product_id, warehouse_id
        ) == 100

        # Failed movement must not exist.
        assert count_movements(test_db) == 0

    finally:
        # Remove simulated failure mechanism.
        with test_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DROP TRIGGER IF EXISTS
                    reject_movement_insert
                    ON stock_movements;
                """)

                cursor.execute("""
                    DROP FUNCTION IF EXISTS
                    reject_test_movement();
                """)
