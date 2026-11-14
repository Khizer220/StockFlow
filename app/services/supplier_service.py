
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


def create_supplier(db: Session, supplier_data: SupplierCreate):
    if supplier_data.email:
        existing_supplier = (
            db.query(Supplier)
            .filter(Supplier.email == supplier_data.email)
            .first()
        )

        if existing_supplier:
            raise ValueError("Supplier email already exists.")

    new_supplier = Supplier(
        name=supplier_data.name,
        email=supplier_data.email,
        phone=supplier_data.phone,
        address=supplier_data.address
    )

    try:
        db.add(new_supplier)
        db.commit()
        db.refresh(new_supplier)
        return new_supplier

    except IntegrityError:
        db.rollback()
        raise ValueError("Supplier email already exists.")


def get_all_suppliers(db: Session):
    return (
        db.query(Supplier)
        .filter(Supplier.is_active == True)
        .order_by(Supplier.id.desc())
        .all()
    )


def get_supplier_by_id(db: Session, supplier_id: int):
    return (
        db.query(Supplier)
        .filter(
            Supplier.id == supplier_id,
            Supplier.is_active == True
        )
        .first()
    )


def update_supplier(
    db: Session,
    supplier_id: int,
    supplier_data: SupplierUpdate
):
    supplier = get_supplier_by_id(db, supplier_id)

    if supplier is None:
        return None

    update_data = supplier_data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] is not None:
        existing_supplier = (
            db.query(Supplier)
            .filter(
                Supplier.email == update_data["email"],
                Supplier.id != supplier_id
            )
            .first()
        )

        if existing_supplier:
            raise ValueError("Supplier email already exists.")

    for field, value in update_data.items():
        setattr(supplier, field, value)

    try:
        db.commit()
        db.refresh(supplier)
        return supplier

    except IntegrityError:
        db.rollback()
        raise ValueError("Supplier email already exists.")


def deactivate_supplier(db: Session, supplier_id: int):
    supplier = get_supplier_by_id(db, supplier_id)

    if supplier is None:
        return None

    supplier.is_active = False

    db.commit()
    db.refresh(supplier)

    return supplier
