
from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel

from database.dashboard import (
    get_dashboard_metrics,
    get_daily_activity
)
from fastapi import Depends

from api.dependencies.auth import (
    require_viewer
)

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


# ==========================================
# RESPONSE MODELS
# ==========================================

class DashboardMetrics(BaseModel):
    active_products: int
    active_warehouses: int
    total_movements: int
    low_stock_alerts: int


class DailyActivity(BaseModel):
    movement_date: date
    entries: int
    exits: int


# ==========================================
# DASHBOARD METRICS
# ==========================================

@router.get(
    "/metrics",
    response_model=DashboardMetrics,
    dependencies=[Depends(require_viewer)]
)
def dashboard_metrics():
    """Return dashboard KPI metrics."""
    return get_dashboard_metrics()


# ==========================================
# DAILY MOVEMENT ACTIVITY
# ==========================================

@router.get(
    "/activity",
    response_model=list[DailyActivity],
    dependencies=[Depends(require_viewer)]
)
def dashboard_activity():
    """Return movement activity for the last 7 days."""
    return get_daily_activity()
