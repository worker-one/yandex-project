from pydantic import BaseModel
from typing import Optional
from datetime import datetime  # Add this import
from app.auth.schemas import UserRead

class ItemBase(BaseModel):
    device_id: str
    name: str
    position: int = 0
    is_online: bool = False
    last_seen: Optional[datetime] = None

class ItemCreate(ItemBase):
    user_id: int

class ItemUpdate(BaseModel):  # Changed inheritance to BaseModel for full flexibility
    device_id: Optional[str] = None
    name: Optional[str] = None
    position: Optional[int] = None
    is_online: Optional[bool] = None
    last_seen: Optional[datetime] = None
    # user_id is generally not updated this way, so omitted. Add if needed.

class ItemRead(ItemBase):
    id: int
    user_id: int  # Added user_id field
    owner: Optional[UserRead] = None
    created_at: datetime  # Added from TimeStampMixin
    updated_at: datetime  # Added from TimeStampMixin

    class Config:
        orm_mode = True

class ItemReadDetails(ItemRead):
    # Fields 'avaliable', 'created_at', 'updated_at' removed as they are covered by ItemRead
    # This class can be used for future detail-specific fields or as an alias.
    pass

# --- Filtering and Sorting ---

class ItemFilter(BaseModel):
    name: Optional[str] = None
    user_id: Optional[int] = None # Changed from owner_id, removed description

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
                        "device_id": "dev_abc123",
                        "name": "Example Item",
                        "position": 0,
                        "is_online": False,
                        "last_seen": "2023-01-01T12:00:00Z", # Example datetime
                        "user_id": 1,
                        "owner": {
                            "id": 1,
                            "email": "user@example.com",
                            # Other UserRead fields if necessary for example
                        },
                        "created_at": "2023-01-01T10:00:00Z", # Example datetime
                        "updated_at": "2023-01-01T11:00:00Z"  # Example datetime
                    }
                ],
                "total": 1
            }
        }