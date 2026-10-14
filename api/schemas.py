
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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
