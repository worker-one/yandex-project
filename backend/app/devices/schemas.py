from pydantic import BaseModel
from typing import Optional
from app.auth.schemas import UserRead

class DeviceBase(BaseModel):
    serial_number: str
    name: str

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    serial_number: Optional[str] = None
    name: Optional[str] = None

class DeviceRead(DeviceBase):
    id: int
    user_id: int
    owner: Optional[UserRead] = None

    class Config:
        orm_mode = True

class DeviceReadDetails(DeviceRead):
    pass

# --- Filtering and Sorting ---

class DeviceFilter(BaseModel):
    name: Optional[str] = None
    user_id: Optional[int] = None

class DeviceSort(BaseModel):
    field: str
    direction: str  # 'asc' or 'desc'

    class Config:
        schema_extra = {
            "example": {
                "field": "name",
                "direction": "asc"
            }
        }

class DeviceListResponse(BaseModel):
    devices: list[DeviceRead]
    total: int

    class Config:
        orm_mode = True

class DeviceQuery(BaseModel):
    name: Optional[str] = None
    user_id: Optional[int] = None

class DevicesListResponse(BaseModel):
    devices: list[DeviceRead]
    total: int

    class Config:
        orm_mode = True