from pydantic import BaseModel
from typing import Optional
from app.auth.schemas import UserRead  # add this import

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    website_url: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemRead(ItemBase):
    id: int
    average_rating: Optional[float] = None
    owner: Optional[UserRead] = None  # add this field

    class Config:
        orm_mode = True

class ItemReadDetails(ItemRead):
    avaliable: Optional[bool] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# --- Filtering and Sorting ---

class ItemFilter(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None

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
        schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "name": "Example Item",
                        "description": "This is an example item.",
                        "image_url": "https://example.com/logo.png",
                        "website_url": "https://example.com",
                        "owner_id": 1
                    }
                ],
                "total": 1
            }
        }