
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_admin

from app.schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse
)

from app.services.inventory_service import (
    create_inventory,
    get_all_inventory,
    get_inventory_by_id,
    get_inventory_by_product_id,
    update_inventory,
    get_low_stock_inventory
)


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_inventory_endpoint(
    inventory_data: InventoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    try:
        return create_inventory(db, inventory_data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


@router.get("/", response_model=list[InventoryResponse])
def get_inventory_endpoint(db: Session = Depends(get_db)):
    return get_all_inventory(db)


@router.get("/low-stock", response_model=list[InventoryResponse])
def get_low_stock_endpoint(db: Session = Depends(get_db)):
    return get_low_stock_inventory(db)


@router.get("/product/{product_id}", response_model=InventoryResponse)
def get_inventory_by_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db)
):
    inventory = get_inventory_by_product_id(db, product_id)

    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found for this product"
        )

    return inventory


@router.get("/{inventory_id}", response_model=InventoryResponse)
def get_inventory_by_id_endpoint(
    inventory_id: int,
    db: Session = Depends(get_db)
):
    inventory = get_inventory_by_id(db, inventory_id)

    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )

    return inventory


@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory_endpoint(
    inventory_id: int,
    inventory_data: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    inventory = update_inventory(db, inventory_id, inventory_data)

    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )

    return inventory
