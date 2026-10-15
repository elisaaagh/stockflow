
from fastapi import APIRouter, HTTPException, status

from api.schemas import (
    MovementCreate,
    MovementCreated,
    MovementResponse
)

from database.movements import (
    register_movement,
    get_movements,
    StockMovementError
)
from fastapi import Depends

from api.dependencies.auth import (
    require_operator,
    require_viewer
)

router = APIRouter(
    prefix="/api/movements",
    tags=["Movements"]
)


# ==========================================
# GET MOVEMENT HISTORY
# ==========================================

@router.get(
    "",
    response_model=list[MovementResponse],
    dependencies=[Depends(require_viewer)]
)
def list_movements():
    return get_movements()


# ==========================================
# CREATE STOCK MOVEMENT
# ==========================================

@router.post(
    "",
    response_model=MovementCreated,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator)]
)
def create_movement(payload: MovementCreate):

    try:
        movement_id = register_movement(
            product_id=payload.product_id,
            warehouse_id=payload.warehouse_id,
            movement_type=payload.movement_type,
            quantity=payload.quantity,
            notes=payload.notes
        )

    except StockMovementError as error:
        message = str(error)

        if "not found" in message.lower():
            http_status = 404
        else:
            http_status = 409

        raise HTTPException(
            status_code=http_status,
            detail=message
        ) from error

    return {
        "movement_id": movement_id,
        "message": "Stock movement registered successfully."
    }
