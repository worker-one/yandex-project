# app/devices/router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload
import uuid

from app.database.core import get_db
from app.devices import schemas as device_schemas
from app.devices import service as device_service
from app import schemas as common_schemas
# auth_service
from app.auth.service import auth_service
from app.dependencies import get_current_active_user
from app.auth.models import User
from app.devices.models import Device


router = APIRouter(
    tags=["Devices"]
)


@router.get("/devices/{device_serial_number}", response_model=device_schemas.DeviceRead)
async def get_device(
    device_serial_number: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific device by its serial number.
    """
    device = device_service.device_service.get_device_by_serial_number(db=db, device_serial_number=device_serial_number, options=[selectinload(Device.owner)])
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device

@router.put("/devices/{device_serial_number}", response_model=device_schemas.DeviceRead)
async def update_device(
    device_serial_number: str,
    device_in: device_schemas.DeviceUpdate,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a device.
    """
    device = device_service.device_service.get_device_by_serial_number(db=db, device_serial_number=device_serial_number, options=[selectinload(Device.owner)])
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if device.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    updated_device = device_service.device_service.update_device(db=db, device=device, device_in=device_in)
    db.refresh(updated_device, attribute_names=["owner"])
    return updated_device

@router.delete("/devices/{device_serial_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_serial_number: str,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a device.
    """
    device = device_service.device_service.get_device_by_serial_number(db=db, device_serial_number=device_serial_number, options=[selectinload(Device.owner)])
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if device.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    device_service.device_service.delete_device(db=db, device=device)
    return None


@router.get("/devices/", response_model=device_schemas.DeviceListResponse)
async def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    name: str = Query(None),
    user_id: int = Query(None),
    sort_field: str = Query("id"),
    sort_direction: str = Query("asc"),
    db: Session = Depends(get_db)
):
    """
    List devices with filtering, sorting, and pagination.
    """
    filters = device_schemas.DeviceFilter(
        name=name,
        user_id=user_id
    )
    sort = device_schemas.DeviceSort(
        field=sort_field,
        direction=sort_direction
    )
    devices = device_service.device_service.list_devices(
        db=db,
        skip=skip,
        limit=limit,
        filters=filters,
        sort=sort,
        options=[selectinload(Device.owner)]
    )
    return devices

@router.post("/devices/", response_model=device_schemas.DeviceRead, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_in: device_schemas.DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new device.
    """
    device = device_service.device_service.create_device(db=db, device_in=device_in, owner_id=current_user.id)
    db.refresh(device, attribute_names=["owner"])
    return device

# Get user's devices list
# GET https://example.com/v1.0/user/devices
@router.get("/user/devices", response_model=device_schemas.UserDevicesResponse)
async def get_user_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's devices with pagination.
    """
    devices_result = device_service.device_service.get_user_devices(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        options=[selectinload(Device.owner)]
    )
    # Transform devices to required format
    def device_to_payload(device):
        return device_schemas.DevicePayloadDevice(
            id=str(device.id),
            name=device.name,
            status_info=device_schemas.DeviceStatusInfo(reportable=True),
            description=f"Device {device.name}",
            room=device.room,
            type=device.type,
            custom_data={},
            capabilities=[
                {
                    "type": "devices.capabilities.on_off"
                }
            ],
            properties=[],    # changed from {} to []
            device_info=device_schemas.DeviceInfo(
                manufacturer="Elkarobotics",
                model="Unknown",
                hw_version="1.0",
                sw_version="1.0"
            )
        )
    payload_devices = [device_to_payload(d) for d in devices_result.devices]
    response = device_schemas.UserDevicesResponse(
        request_id=str(uuid.uuid4()),
        payload=device_schemas.UserDevicesPayload(
            user_id=str(current_user.id),
            devices=payload_devices
        )
    )
    return response

# Get user's devices status with query parameters
# POST https://example.com/v1.0/user/devices/query
@router.post("/user/devices/query", response_model=device_schemas.DevicesListResponse)
async def query_user_devices(
    query: device_schemas.DeviceQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Query user's devices with filters.
    """
    devices = device_service.device_service.query_user_devices(db=db, user_id=current_user.id, filters=query)
    return devices

# Change device status
# POST https://example.com/v1.0/user/devices/action
@router.post("/user/devices/action", response_model=device_schemas.DevicesListResponse)
async def change_device_status(
    #action: device_schemas.DeviceAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Change device status.
    """
    # Implement the logic to change device status based on the action
    # This is a placeholder implementation
    #devices = device_service.device_service.change_device_status(db=db, user_id=current_user.id, action=action)
    # Mock implementation for demonstration
    devices = device_service.device_service.get_user_devices(
        db=db,
        user_id=current_user.id,
        options=[selectinload(Device.owner)]
    )
    return devices

 
# Unlink account
# POST https://example.com/v1.0/user/unlink
@router.post("/user/unlink", response_model=common_schemas.Message, status_code=status.HTTP_200_OK)
def unlink_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Unlink the user's Yandex account.
    """
    auth_service.unlink_yandex_account(db=db, user=current_user)
    return common_schemas.Message(message="OK")
