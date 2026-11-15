
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    DateTime,
    Numeric,
    Enum,
    func,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Order(Base):
    __tablename__ = "orders"

    __table_args__ = (
        CheckConstraint(
            "total_amount >= 0",
            name="check_order_total_non_negative"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        Enum("PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"),
        default="PENDING",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    customer = relationship("Customer")

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="check_order_item_quantity_positive"
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="check_order_item_price_non_negative"
        ),
        CheckConstraint(
            "subtotal >= 0",
            name="check_order_item_subtotal_non_negative"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    order = relationship(
        "Order",
        back_populates="items"
    )

    product = relationship("Product")
