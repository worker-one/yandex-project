from pydantic import BaseModel
from typing import Any, Dict, List, Optional
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

class DeviceStatusInfo(BaseModel):
    reportable: bool

class DeviceInfo(BaseModel):
    manufacturer: str
    model: str
    hw_version: str
    sw_version: str

class DevicePayloadDevice(BaseModel):
    id: str
    name: str
    status_info: DeviceStatusInfo
    description: str
    room: str
    type: str
    custom_data: Dict[str, Any]
    capabilities: Dict[str, Any]
    properties: Dict[str, Any]
    device_info: DeviceInfo

class UserDevicesPayload(BaseModel):
    user_id: str
    devices: List[DevicePayloadDevice]

class UserDevicesResponse(BaseModel):
    request_id: str
    payload: UserDevicesPayload