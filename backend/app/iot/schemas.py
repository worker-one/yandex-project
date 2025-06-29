from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Schemas for Device Info
class DeviceInfo(BaseModel):
    manufacturer: str
    model: str
    hw_version: str
    sw_version: str

# Schemas for Capabilities
class CapabilityParameters(BaseModel):
    split: Optional[bool] = None
    instance: Optional[str] = None
    name: Optional[str] = None
    unit: Optional[str] = None
    random_access: Optional[bool] = None
    range: Optional[Dict[str, int]] = None

class Capability(BaseModel):
    type: str
    retrievable: bool
    reportable: bool
    parameters: CapabilityParameters

# Main Device Schema
class Device(BaseModel):
    id: str
    serial_number: str = None
    name: str
    description: Optional[str] = None
    room: Optional[str] = None
    type: str
    capabilities: List[Capability]
    device_info: Optional[DeviceInfo] = None

# Schemas for Yandex Dialogs API
class UserDevicesPayload(BaseModel):
    user_id: str
    devices: List[Device]

class UserDevicesResponse(BaseModel):
    request_id: str
    payload: UserDevicesPayload

class UnlinkResponse(BaseModel):
    request_id: str
