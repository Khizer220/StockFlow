
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user import User
from app.schemas.stock_movement import StockMovementCreate


def create_stock_movement(
    db: Session,
    movement_data: StockMovementCreate,
    current_user: User
):
    try:
        # Verify that the product exists and is active.
        product = db.execute(
            select(Product)
            .where(
                Product.id == movement_data.product_id,
                Product.is_active == True
            )
            .with_for_update()
        ).scalar_one_or_none()

        if product is None:
            raise ValueError("Active product not found.")

        # Lock the inventory record during this transaction.
        inventory = db.execute(
            select(Inventory)
            .where(Inventory.product_id == movement_data.product_id)
            .with_for_update()
        ).scalar_one_or_none()

        if inventory is None:
            raise ValueError("Inventory record not found.")

        quantity_before = inventory.quantity

        if movement_data.movement_type == "IN":
            quantity_after = quantity_before + movement_data.quantity

        elif movement_data.movement_type == "OUT":
            quantity_after = quantity_before - movement_data.quantity

            if quantity_after < 0:
                raise ValueError("Insufficient stock available.")

        elif movement_data.movement_type == "ADJUSTMENT":
            # ADJUSTMENT sets stock to the physical count.
            quantity_after = movement_data.quantity

        else:
            raise ValueError("Invalid stock movement type.")
        movement_quantity = abs(quantity_after - quantity_before)

        if movement_quantity == 0:
            raise ValueError("Stock movement would not change the quantity.")

        # Update current inventory.
        inventory.quantity = quantity_after

        # Record the movement history.
        new_movement = StockMovement(
            product_id=movement_data.product_id,
            user_id=current_user.id,
            movement_type=movement_data.movement_type,
            quantity=movement_quantity,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reason=movement_data.reason
        )

        db.add(new_movement)
        db.commit()
        db.refresh(new_movement)

        return new_movement

    except Exception:
        db.rollback()
        raise


def get_stock_movements(db: Session):
    return (
        db.query(StockMovement)
        .order_by(StockMovement.created_at.desc(), StockMovement.id.desc())
        .all()
    )


def get_stock_movements_by_product(
    db: Session,
    product_id: int
):
    return (
        db.query(StockMovement)
        .filter(StockMovement.product_id == product_id)
        .order_by(StockMovement.created_at.desc(), StockMovement.id.desc())
        .all()
    )
