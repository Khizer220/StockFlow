
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


def create_customer(db: Session, customer_data: CustomerCreate):
    customer = Customer(**customer_data.model_dump())

    try:
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    except IntegrityError as error:
        db.rollback()
        raise ValueError("A customer with this email already exists.") from error


def get_all_customers(db: Session):
    return (
        db.query(Customer)
        .filter(Customer.is_active.is_(True))
        .order_by(Customer.id.desc())
        .all()
    )


def get_customer_by_id(db: Session, customer_id: int):
    return (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.is_active.is_(True)
        )
        .first()
    )


def update_customer(
    db: Session,
    customer_id: int,
    customer_data: CustomerUpdate
):
    customer = get_customer_by_id(db, customer_id)

    if customer is None:
        raise ValueError("Customer not found.")

    update_data = customer_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(customer, field, value)

    try:
        db.commit()
        db.refresh(customer)
        return customer

    except IntegrityError as error:
        db.rollback()
        raise ValueError("A customer with this email already exists.") from error


def deactivate_customer(db: Session, customer_id: int):
    customer = get_customer_by_id(db, customer_id)

    if customer is None:
        raise ValueError("Customer not found.")

    customer.is_active = False

    db.commit()
    db.refresh(customer)

    return customer
