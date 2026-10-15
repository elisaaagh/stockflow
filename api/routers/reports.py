
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from database.reports import get_movement_report


router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"]
)


# ==========================================
# RESPONSE MODEL
# ==========================================

class MovementReportResponse(BaseModel):
    movement_id: int
    created_at: datetime
    sku: str
    product: str
    warehouse: str
    movement_type: Literal["IN", "OUT"]
    quantity: Decimal
    unit: str
    notes: str | None = None


# ==========================================
# MOVEMENT REPORT
# ==========================================

@router.get(
    "/movements",
    response_model=list[MovementReportResponse]
)
def movement_report(
    start_date: date,
    end_date: date,
    warehouse_id: int | None = Query(
        default=None,
        gt=0
    ),
    product_id: int | None = Query(
        default=None,
        gt=0
    ),
    movement_type: Literal["IN", "OUT"] | None = None
):
    """Retrieve filtered stock movement reports."""

    if start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="Start date must be before end date."
        )

    return get_movement_report(
        start_date=start_date,
        end_date=end_date,
        warehouse_id=warehouse_id,
        product_id=product_id,
        movement_type=movement_type
    )
