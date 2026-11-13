
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# Schema for creating a product
class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)

    sku: str = Field(min_length=3, max_length=50)

    description: str | None = Field(
        default=None,
        max_length=500
    )

    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


# Schema for returning product information
class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    description: str | None
    price: Decimal
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)

    sku: str = Field(min_length=3, max_length=50)

    description: str | None = Field(
        default=None,
        max_length=500
    )

    price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2
    )
