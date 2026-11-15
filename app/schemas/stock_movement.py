
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class StockMovementCreate(BaseModel):
    product_id: int = Field(gt=0)

    movement_type: Literal["IN", "OUT", "ADJUSTMENT"]

    quantity: int = Field(gt=0)

    reason: str | None = Field(
        default=None,
        max_length=255
    )


class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    movement_type: str
    quantity: int
    quantity_before: int
    quantity_after: int
    reason: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)