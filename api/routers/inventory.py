
from fastapi import APIRouter, Query

from database.inventory import (
    get_warehouses,
    get_inventory,
    get_low_stock
)
from fastapi import Depends

from api.dependencies.auth import (
    require_viewer
)


router = APIRouter(tags=["Inventory"])


# ==========================================
# GET WAREHOUSES
# ==========================================

@router.get(
        "/api/warehouses",
        dependencies=[Depends(require_viewer)]
    )
def list_warehouses():
    """Return all registered warehouses."""

    return get_warehouses()


# ==========================================
# GET INVENTORY
# ==========================================

@router.get(
        "/api/inventory",
        dependencies=[Depends(require_viewer)]
    )
def list_inventory(
    warehouse_id: int | None = Query(
        default=None,
        gt=0,
        description="Filter inventory by warehouse ID"
    )
):
    """Return inventory, optionally filtered by warehouse."""

    inventory = get_inventory()

    if warehouse_id is not None:
        inventory = [
            item
            for item in inventory
            if item["warehouse_id"] == warehouse_id
        ]

    return inventory


# ==========================================
# GET LOW STOCK
# ==========================================

@router.get(
        "/api/inventory/low-stock",
        dependencies=[Depends(require_viewer)]
    )
def list_low_stock():
    """Return active products below minimum stock."""

    return get_low_stock()
