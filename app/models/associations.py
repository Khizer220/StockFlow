from sqlalchemy import Table, Column, Integer, ForeignKey

from app.database.session import Base


product_suppliers = Table(
    "product_suppliers",
    Base.metadata,

    Column(
        "product_id",
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True
    ),

    Column(
        "supplier_id",
        Integer,
        ForeignKey("suppliers.id", ondelete="CASCADE"),
        primary_key=True
    )
)