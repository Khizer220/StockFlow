
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inventory import InventoryCreate, InventoryUpdate


def create_inventory(db: Session, inventory_data: InventoryCreate):
    product = (
        db.query(Product)
        .filter(
            Product.id == inventory_data.product_id,
            Product.is_active == True
        )
        .first()
    )

    if product is None:
        raise ValueError("Active product not found.")

    existing_inventory = (
        db.query(Inventory)
        .filter(Inventory.product_id == inventory_data.product_id)
        .first()
    )

    if existing_inventory:
        raise ValueError("Inventory already exists for this product.")

    new_inventory = Inventory(
        product_id=inventory_data.product_id,
        quantity=inventory_data.quantity,
        reorder_level=inventory_data.reorder_level
    )

    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)

    return new_inventory


def get_all_inventory(db: Session):
    return (
        db.query(Inventory)
        .join(Product)
        .filter(Product.is_active == True)
        .order_by(Inventory.id.desc())
        .all()
    )


def get_inventory_by_id(db: Session, inventory_id: int):
    return (
        db.query(Inventory)
        .join(Product)
        .filter(
            Inventory.id == inventory_id,
            Product.is_active == True
        )
        .first()
    )


def get_inventory_by_product_id(db: Session, product_id: int):
    return (
        db.query(Inventory)
        .join(Product)
        .filter(
            Inventory.product_id == product_id,
            Product.is_active == True
        )
        .first()
    )


def update_inventory(
    db: Session,
    inventory_id: int,
    inventory_data: InventoryUpdate
):
    inventory = get_inventory_by_id(db, inventory_id)

    if inventory is None:
        return None

    update_data = inventory_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(inventory, field, value)

    db.commit()
    db.refresh(inventory)

    return inventory


def get_low_stock_inventory(db: Session):
    return (
        db.query(Inventory)
        .join(Product)
        .filter(
            Product.is_active == True,
            Inventory.quantity <= Inventory.reorder_level
        )
        .order_by(Inventory.quantity.asc())
        .all()
    )
