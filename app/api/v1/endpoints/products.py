
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_admin

from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate
)

from app.services.product_service import (
    create_product,
    delete_product,
    get_all_products,
    get_product_by_id,
    update_product
)


router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product_endpoint(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    try:
        return create_product(db, product_data)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


@router.get("/", response_model=list[ProductResponse])
def get_products_endpoint(
    db: Session = Depends(get_db)
):
    return get_all_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = get_product_by_id(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product_endpoint(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    try:
        product = update_product(
            db,
            product_id,
            product_data
        )

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        return product

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


@router.delete("/{product_id}")
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    deleted_product = delete_product(db, product_id)

    if deleted_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return {
        "message": "Product deactivated successfully",
        "product_id": product_id,
        "is_active": deleted_product.is_active
    }

