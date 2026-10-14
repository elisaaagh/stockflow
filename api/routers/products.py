
from fastapi import APIRouter, HTTPException, status
from psycopg.errors import UniqueViolation
from pydantic import field_validator

from api.schemas import ProductCreate, ProductResponse
from database.products import (
    get_all_products,
    get_product_by_id,
    create_product
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
    response_model=list[ProductResponse]
)
def list_products():
    return get_all_products()


# ==========================================
# GET PRODUCT BY ID
# ==========================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse
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
