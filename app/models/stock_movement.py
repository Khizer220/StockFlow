
from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    CheckConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="check_stock_movement_quantity_positive"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    movement_type: Mapped[str] = mapped_column(
        Enum("IN", "OUT", "ADJUSTMENT"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    quantity_before: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0"
    )

    quantity_after: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0"
    )

    reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    product = relationship("Product")

    user = relationship("User")
