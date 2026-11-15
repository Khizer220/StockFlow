
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_admin

from app.schemas.stock_movement import (
    StockMovementCreate,
    StockMovementResponse
)

from app.services.stock_movement_service import (
    create_stock_movement,
    get_stock_movements,
    get_stock_movements_by_product
)


router = APIRouter(
    prefix="/stock-movements",
    tags=["Stock Movements"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED
)
def create_stock_movement_endpoint(
    movement_data: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    try:
        return create_stock_movement(
            db,
            movement_data,
            current_user
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        ) from error


@router.get("/", response_model=list[StockMovementResponse])
def get_stock_movements_endpoint(
    db: Session = Depends(get_db)
):
    return get_stock_movements(db)


@router.get(
    "/product/{product_id}",
    response_model=list[StockMovementResponse]
)
def get_stock_movements_by_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db)
):
    return get_stock_movements_by_product(db, product_id)
