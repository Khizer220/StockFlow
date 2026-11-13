
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    sku: Mapped[str] = mapped_column(
    String(50),
    unique=True,
    nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
    Boolean,
    default=True,
    nullable=False
    )