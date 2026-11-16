
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    update_order_status,
    count_orders
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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return create_order(db, order_data, current_user)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        ) from error


@router.get("/")
def get_all_orders_endpoint(
    search: str | None = None,
    order_status: str | None = Query(default=None, alias="status"),
    customer_id: int | None = Query(default=None, gt=0),
    min_total: Decimal | None = Query(default=None, ge=0),
    max_total: Decimal | None = Query(default=None, ge=0),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    db: Session = Depends(get_db)
):
    if min_total is not None and max_total is not None:
        if min_total > max_total:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum total cannot exceed maximum total."
            )

    try:
        orders = get_all_orders(
            db=db,
            search=search,
            status=order_status,
            customer_id=customer_id,
            min_total=min_total,
            max_total=max_total,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )

        total = count_orders(
            db=db,
            search=search,
            status=order_status,
            customer_id=customer_id,
            min_total=min_total,
            max_total=max_total
        )

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "orders": orders
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        ) from error


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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return update_order_status(
            db,
            order_id,
            status_data,
            current_user
        )

    except ValueError as error:
        error_status = (
            status.HTTP_404_NOT_FOUND
            if str(error) == "Order not found."
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(
            status_code=error_status,
            detail=str(error)
        ) from error
