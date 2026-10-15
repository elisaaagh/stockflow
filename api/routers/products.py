
from fastapi import APIRouter, HTTPException, status
from psycopg.errors import UniqueViolation
from pydantic import field_validator

from api.schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ProductPatch,
    ProductStatusUpdate
)

from database.products import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    change_product_status
)
from fastapi import Depends

from api.dependencies.auth import (
    require_admin,
    require_viewer
)

router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


# ==========================================
# GET ALL PRODUCTS
# ==========================================

@router.get(
    "",
    response_model=list[ProductResponse],
    dependencies=[Depends(require_viewer)]
)
def list_products():
    return get_all_products()


# ==========================================
# GET PRODUCT BY ID
# ==========================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(require_viewer)]
)
def read_product(product_id: int):

    product = get_product_by_id(product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    return product


# ==========================================
# CREATE PRODUCT
# ==========================================

@router.post(
    "",
    response_model=ProductResponse,
    dependencies=[Depends(require_admin)],
    status_code=status.HTTP_201_CREATED
)
def add_product(product: ProductCreate):

    sku = product.sku.strip().upper()
    name = product.name.strip()
    unit = product.unit.strip()
    description = (
        product.description.strip()
        if product.description
        else None
    )

    if not sku or not name or not unit:
        raise HTTPException(
            status_code=422,
            detail="SKU, name and unit are required."
        )

    try:
        product_id = create_product(
            sku=sku,
            name=name,
            description=description,
            unit=unit,
            min_stock=product.min_stock
        )

    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="A product with this SKU already exists."
        )

    return get_product_by_id(product_id)

# ==========================================
# PUT - FULL PRODUCT UPDATE
# ==========================================

@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(require_admin)]
)
def replace_product(
    product_id: int,
    product: ProductUpdate
):
    current = get_product_by_id(product_id)

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    updated = update_product(
        product_id=product_id,
        name=product.name,
        description=product.description,
        unit=product.unit,
        min_stock=product.min_stock
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    return get_product_by_id(product_id)

# ==========================================
# PATCH - PARTIAL PRODUCT UPDATE
# ==========================================

@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(require_admin)]
)
def patch_product(
    product_id: int,
    changes: ProductPatch
):
    current = get_product_by_id(product_id)

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    updates = changes.model_dump(
        exclude_unset=True
    )

    if not updates:
        raise HTTPException(
            status_code=422,
            detail="At least one field is required."
        )

    required_fields = {"name", "unit", "min_stock"}

    for field in required_fields:
        if field in updates and updates[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null."
            )

    name = updates.get("name", current["name"])
    description = updates.get(
        "description",
        current["description"]
    )
    unit = updates.get("unit", current["unit"])
    min_stock = updates.get(
        "min_stock",
        current["min_stock"]
    )

    updated = update_product(
        product_id=product_id,
        name=name,
        description=description,
        unit=unit,
        min_stock=min_stock
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    return get_product_by_id(product_id)

# ==========================================
# PATCH - ACTIVATE / DEACTIVATE PRODUCT
# ==========================================

@router.patch(
    "/{product_id}/status",
    response_model=ProductResponse,
    dependencies=[Depends(require_admin)]
)
def update_product_status(
    product_id: int,
    payload: ProductStatusUpdate
):
    updated = change_product_status(
        product_id=product_id,
        is_active=payload.is_active
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    return get_product_by_id(product_id)
