from pydantic import BaseModel
from typing import Optional
from app.auth.schemas import UserRead

class ItemBase(BaseModel):
    serial_number: str
    name: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    serial_number: Optional[str] = None
    name: Optional[str] = None

class ItemRead(ItemBase):
    id: int
    user_id: int
    owner: Optional[UserRead] = None

    class Config:
        orm_mode = True

class ItemReadDetails(ItemRead):
    pass

# --- Filtering and Sorting ---

class ItemFilter(BaseModel):
    name: Optional[str] = None
    user_id: Optional[int] = None

class ItemSort(BaseModel):
    field: str
    direction: str  # 'asc' or 'desc'

    class Config:
        schema_extra = {
            "example": {
                "field": "name",
                "direction": "asc"
            }
        }

class ItemListResponse(BaseModel):
    items: list[ItemRead]
    total: int

    class Config:
        orm_mode = True