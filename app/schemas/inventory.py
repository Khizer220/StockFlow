
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, model_validator


class InventoryCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)


class InventoryUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")

        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null.")

        return self


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    reorder_level: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
