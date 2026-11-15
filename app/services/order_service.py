
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.models.user import User

from app.schemas.order import OrderCreate, OrderStatusUpdate


def create_order(
    db: Session,
    order_data: OrderCreate,
    current_user: User
):
    # Validate customer.
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == order_data.customer_id,
            Customer.is_active.is_(True)
        )
        .first()
    )

    if customer is None:
        raise ValueError("Active customer not found.")

    # Reject duplicate products.
    product_ids = [item.product_id for item in order_data.items]

    if len(product_ids) != len(set(product_ids)):
        raise ValueError("Duplicate products are not allowed in an order.")

    try:
        order_items = []
        total_amount = Decimal("0.00")

        sorted_product_ids = sorted(product_ids)

        # STEP 1: Lock products first.
        products = (
            db.execute(
                select(Product)
                .where(
                    Product.id.in_(sorted_product_ids),
                    Product.is_active.is_(True)
                )
                .order_by(Product.id)
                .with_for_update()
            )
            .scalars()
            .all()
        )

        product_map = {
            product.id: product
            for product in products
        }

        # STEP 2: Lock inventory records second.
        inventory_records = (
            db.execute(
                select(Inventory)
                .where(
                    Inventory.product_id.in_(sorted_product_ids)
                )
                .order_by(Inventory.product_id)
                .with_for_update()
            )
            .scalars()
            .all()
        )

        inventory_map = {
            inventory.product_id: inventory
            for inventory in inventory_records
        }

        # STEP 3: Validate all products and stock.
        for item in order_data.items:
            product = product_map.get(item.product_id)

            if product is None:
                raise ValueError(
                    f"Active product with ID {item.product_id} not found."
                )

            inventory = inventory_map.get(item.product_id)

            if inventory is None:
                raise ValueError(
                    f"Inventory record not found for product {item.product_id}."
                )

            if inventory.quantity < item.quantity:
                raise ValueError(
                    f"Insufficient stock for product {item.product_id}. "
                    f"Available: {inventory.quantity}, "
                    f"Requested: {item.quantity}."
                )

        # STEP 4: Deduct stock and create OUT movements.
        for item in order_data.items:
            product = product_map[item.product_id]
            inventory = inventory_map[item.product_id]

            quantity_before = inventory.quantity
            quantity_after = quantity_before - item.quantity

            inventory.quantity = quantity_after

            unit_price = Decimal(str(product.price))
            subtotal = unit_price * item.quantity
            total_amount += subtotal

            order_items.append(
                OrderItem(
                    product_id=product.id,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    subtotal=subtotal
                )
            )

            db.add(
                StockMovement(
                    product_id=product.id,
                    user_id=current_user.id,
                    movement_type="OUT",
                    quantity=item.quantity,
                    quantity_before=quantity_before,
                    quantity_after=quantity_after,
                    reason="Stock deducted for order"
                )
            )

        # STEP 5: Create order.
        new_order = Order(
            customer_id=customer.id,
            total_amount=total_amount,
            items=order_items
        )

        db.add(new_order)

        # STEP 6: Commit everything together.
        db.commit()
        db.refresh(new_order)

        return get_order_by_id(db, new_order.id)

    except Exception:
        db.rollback()
        raise


def get_all_orders(db: Session):
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .order_by(Order.created_at.desc(), Order.id.desc())
        .all()
    )


def get_order_by_id(db: Session, order_id: int):
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )


def update_order_status(
    db: Session,
    order_id: int,
    status_data: OrderStatusUpdate,
    current_user: User
):
    try:
        # Lock order to prevent simultaneous status changes.
        order = (
            db.execute(
                select(Order)
                .where(Order.id == order_id)
                .with_for_update()
            )
            .scalar_one_or_none()
        )

        if order is None:
            raise ValueError("Order not found.")

        allowed_transitions = {
            "PENDING": {"CONFIRMED", "CANCELLED"},
            "CONFIRMED": {"COMPLETED", "CANCELLED"},
            "COMPLETED": set(),
            "CANCELLED": set()
        }

        if status_data.status not in allowed_transitions[order.status]:
            raise ValueError(
                f"Cannot change order status from "
                f"{order.status} to {status_data.status}."
            )

        # Restore inventory when cancelling an order.
        if status_data.status == "CANCELLED":

            product_ids = sorted({
                item.product_id for item in order.items
            })

            # Lock inventory records in consistent order.
            inventory_records = (
                db.execute(
                    select(Inventory)
                    .where(Inventory.product_id.in_(product_ids))
                    .order_by(Inventory.product_id)
                    .with_for_update()
                )
                .scalars()
                .all()
            )

            inventory_map = {
                inventory.product_id: inventory
                for inventory in inventory_records
            }

            for item in order.items:
                inventory = inventory_map.get(item.product_id)

                if inventory is None:
                    raise ValueError(
                        f"Inventory record not found for product "
                        f"{item.product_id}."
                    )

                quantity_before = inventory.quantity
                quantity_after = quantity_before + item.quantity

                inventory.quantity = quantity_after

                db.add(
                    StockMovement(
                        product_id=item.product_id,
                        user_id=current_user.id,
                        movement_type="IN",
                        quantity=item.quantity,
                        quantity_before=quantity_before,
                        quantity_after=quantity_after,
                        reason=f"Stock restored for cancelled order #{order.id}"
                    )
                )

        order.status = status_data.status

        db.commit()
        db.refresh(order)

        return get_order_by_id(db, order.id)

    except Exception:
        db.rollback()
        raise
        