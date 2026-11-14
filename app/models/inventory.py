
from datetime import datetime

from sqlalchemy import (
    Integer,
    ForeignKey,
    DateTime,
    CheckConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Inventory(Base):
    __tablename__ = "inventory"

    __table_args__ = (
        CheckConstraint(
            "quantity >= 0",
            name="check_inventory_quantity_non_negative"
        ),
        CheckConstraint(
            "reorder_level >= 0",
            name="check_inventory_reorder_level_non_negative"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        unique=True,
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    reorder_level: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="inventory"
    )