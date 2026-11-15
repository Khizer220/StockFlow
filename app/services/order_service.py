
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderStatusUpdate


def create_order(db: Session, order_data: OrderCreate):
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

    # Reject duplicate products in the same order.
    product_ids = [item.product_id for item in order_data.items]

    if len(product_ids) != len(set(product_ids)):
        raise ValueError("Duplicate products are not allowed in an order.")

    order_items = []
    total_amount = Decimal("0.00")

    try:
        for item in order_data.items:
            product = (
                db.query(Product)
                .filter(
                    Product.id == item.product_id,
                    Product.is_active.is_(True)
                )
                .first()
            )

            if product is None:
                raise ValueError(
                    f"Active product with ID {item.product_id} not found."
                )

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

        new_order = Order(
            customer_id=customer.id,
            total_amount=total_amount,
            items=order_items
        )

        db.add(new_order)
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
    status_data: OrderStatusUpdate
):
    order = get_order_by_id(db, order_id)

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

    try:
        order.status = status_data.status

        db.commit()
        db.refresh(order)

        return get_order_by_id(db, order.id)

    except Exception:
        db.rollback()
        raise

