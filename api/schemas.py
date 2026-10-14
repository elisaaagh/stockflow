
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from typing import Annotated

from pydantic import BeforeValidator


# ==========================================
# PRODUCT RESPONSE
# ==========================================

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    sku: str
    name: str
    description: str | None = None
    unit: str
    min_stock: Decimal
    is_active: bool


# ==========================================
# CREATE PRODUCT REQUEST
# ==========================================

class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    unit: str = Field(min_length=1, max_length=20)
    min_stock: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        max_digits=12,
        decimal_places=2
    )

def validate_text(value):
    if not isinstance(value, str):
        raise ValueError("A text value is required.")

    value = value.strip()

    if not value:
        raise ValueError("Text cannot be empty.")

    return value


NonEmptyText = Annotated[
    str,
    BeforeValidator(validate_text)
]


class ProductUpdate(BaseModel):
    """Complete update of editable product fields."""

    name: NonEmptyText = Field(max_length=150)
    description: str | None
    unit: NonEmptyText = Field(max_length=20)
    min_stock: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2
    )


class ProductPatch(BaseModel):
    """Partial update of editable product fields."""

    name: NonEmptyText | None = Field(
        default=None,
        max_length=150
    )
    description: str | None = None
    unit: NonEmptyText | None = Field(
        default=None,
        max_length=20
    )
    min_stock: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2
    )

class ProductStatusUpdate(BaseModel):
    """Request model for product activation."""

    is_active: bool


from datetime import datetime
from typing import Literal


class MovementCreate(BaseModel):
    """Request model for stock movements."""

    product_id: int = Field(gt=0)
    warehouse_id: int = Field(gt=0)

    movement_type: Literal["IN", "OUT"]

    quantity: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )

    notes: str = Field(
        default="",
        max_length=500
    )


class MovementCreated(BaseModel):
    """Response after creating a movement."""

    movement_id: int
    message: str


class MovementResponse(BaseModel):
    """Movement history response."""

    movement_id: int
    created_at: datetime
    sku: str
    product: str
    warehouse: str
    movement_type: Literal["IN", "OUT"]
    quantity: Decimal
    unit: str
    notes: str | None = None
