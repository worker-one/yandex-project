from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from app.auth.schemas import UserRead

class DeviceBase(BaseModel):
    name: str
    serial_number: str  # Added
    room: Optional[str] = "main"

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    serial_number: Optional[str] = None  # Added
    status: Optional[str] = "off"
    room: Optional[str] = None

class DeviceRead(DeviceBase):
    id: int
    user_id: int
    owner: Optional[UserRead] = None
    status: Optional[str] = "off"  # 'on' or 'off'
    room : Optional[str] = "Спальня"
    type: Optional[str] = "devices.types.openable.curtain"
    custom_data: Dict[str, Any] = {}

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
    type: str = "devices.types.openable.curtain"
    custom_data: Dict[str, Any]
    capabilities: List[Any]  # changed from Dict[str, Any] to List[Any]
    properties: List[Any]    # changed from Dict[str, Any] to List[Any]
    device_info: DeviceInfo

class UserDevicesPayload(BaseModel):
    user_id: str
    devices: List[DevicePayloadDevice]

class UserDevicesResponse(BaseModel):
    request_id: str
    payload: UserDevicesPayload

class DeviceActionCapability(BaseModel):
    type: str
    state: Optional[dict] = None

class DeviceActionDevice(BaseModel):
    id: str
    custom_data: Dict[str, Any]
    capabilities: List[DeviceActionCapability]

class UserDevicesActionPayload(BaseModel):
    devices: List[DeviceActionDevice]

class UserDevicesActionResponse(BaseModel):
    payload: UserDevicesActionPayload