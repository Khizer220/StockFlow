
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user

from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate
)

from app.services.order_service import (
    create_order,
    get_all_orders,
    get_order_by_id,
    update_order_status
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order_endpoint(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_order(db, order_data)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        ) from error


@router.get("/", response_model=list[OrderResponse])
def get_all_orders_endpoint(
    db: Session = Depends(get_db)
):
    return get_all_orders(db)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id_endpoint(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = get_order_by_id(db, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )

    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status_endpoint(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    try:
        return update_order_status(db, order_id, status_data)

    except ValueError as error:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if str(error) == "Order not found."
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(error)
        ) from error
