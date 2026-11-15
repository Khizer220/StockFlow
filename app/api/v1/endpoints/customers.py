
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_admin

from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse
)

from app.services.customer_service import (
    create_customer,
    get_all_customers,
    get_customer_by_id,
    update_customer,
    deactivate_customer
)


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_customer_endpoint(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    try:
        return create_customer(db, customer_data)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


@router.get("/", response_model=list[CustomerResponse])
def get_all_customers_endpoint(
    db: Session = Depends(get_db)
):
    return get_all_customers(db)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_by_id_endpoint(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = get_customer_by_id(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )

    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer_endpoint(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    try:
        return update_customer(db, customer_id, customer_data)

    except ValueError as error:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if str(error) == "Customer not found."
            else status.HTTP_409_CONFLICT
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(error)
        ) from error


@router.delete("/{customer_id}", response_model=CustomerResponse)
def deactivate_customer_endpoint(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    try:
        return deactivate_customer(db, customer_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error
