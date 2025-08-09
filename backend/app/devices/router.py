# app/devices/router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session, selectinload
import uuid
from pydantic import BaseModel
from typing import List

from app.database.core import get_db
from app.devices import models as device_models
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


@router.get("/devices/{device_id}", response_model=device_schemas.DeviceRead)
async def get_device(
    device_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific device by its ID.
    """
    try:
        device_id_int = int(device_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid device ID format")
    
    device = device_service.device_service.get_device_by_id(db=db, device_id=device_id_int, options=[selectinload(Device.owner)])
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device

@router.put("/devices/{device_id}", response_model=device_schemas.DeviceRead)
async def update_device(
    device_id: str,
    device_in: device_schemas.DeviceUpdate,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a device.
    """
    try:
        device_id_int = int(device_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid device ID format")
    
    device = device_service.device_service.get_device_by_id(db=db, device_id=device_id_int, options=[selectinload(Device.owner)])
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if device.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    updated_device = device_service.device_service.update_device(db=db, device=device, device_in=device_in)
    db.refresh(updated_device, attribute_names=["owner", "serial_number_obj"])
    return updated_device

@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a device.
    """
    try:
        device_id_int = int(device_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid device ID format")
    
    device = device_service.device_service.get_device_by_id(db=db, device_id=device_id_int, options=[selectinload(Device.owner)])
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
    
    The serial_number must be in the format SNXXXXXXXXXXXXX (SN followed by 13 digits).
    The serial number must exist in the database and be available for binding.
    """
    try:
        device = device_service.device_service.create_device(db=db, device_in=device_in, owner_id=current_user.id)
        db.refresh(device, attribute_names=["owner"])
        return device
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/devices/{device_id}/commands", response_model=device_schemas.DeviceCommandListResponse)
async def get_device_commands(
    device_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get commands for a specific device.
    """
    device = device_service.device_service.get_device_by_id(db=db, device_id=device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if device.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    commands = device_service.device_service.get_device_commands(db=db, device_id=device_id, skip=skip, limit=limit)
    return commands


@router.get("/devices/{device_id}/events", response_model=device_schemas.DeviceEventListResponse)
async def get_device_events(
    device_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get events for a specific device.
    """
    device = device_service.device_service.get_device_by_id(db=db, device_id=device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if device.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    events = device_service.device_service.get_device_events(db=db, device_id=device_id, skip=skip, limit=limit)
    return events


@router.get("/serial-numbers/", response_model=device_schemas.SerialNumberListResponse)
async def get_serial_numbers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all serial numbers with their status. (Admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    result = device_service.device_service.get_all_serial_numbers(db=db, skip=skip, limit=limit)
    return device_schemas.SerialNumberListResponse(
        serial_numbers=[device_schemas.SerialNumberRead.model_validate(sn, from_attributes=True) for sn in result['serial_numbers']],
        total=result['total']
    )

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
        options=[selectinload(Device.owner), selectinload(Device.serial_number_obj)]
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
                serial_number=device.serial_number or "Unknown",
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
from ..mqtt import mqtt_client
import json

class DeviceActionRequestCapability(device_schemas.DeviceActionCapability):
    state: dict

class DeviceActionRequestDevice(BaseModel):
    id: str
    capabilities: List[DeviceActionRequestCapability]

class UserDevicesActionRequestPayload(BaseModel):
    devices: List[DeviceActionRequestDevice]

class UserDevicesActionRequest(BaseModel):
    payload: UserDevicesActionRequestPayload

@router.post("/user/devices/action", response_model=device_schemas.UserDevicesActionResponse)
async def change_device_status(
    request: UserDevicesActionRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Change device status (Yandex Smart Home compliant).
    
    Example request body:
    
    ```json
    {
    "payload": {
        "devices": [
        {
            "id": "1",
            "capabilities": [
            {
                "type": "devices.capabilities.on_off",
                "state": {
                    "instance": "on",
                    "value": true
                }
            }
            ]
        }
        ]
    }
    ```

    """
    response_devices = []
    for req_device in request.payload.devices:
        device = device_service.device_service.get_device_by_id(db=db, device_id=int(req_device.id))
        if not device or device.user_id != current_user.id:
            continue  # skip devices not found or not owned
        device_capabilities = []
        for cap in req_device.capabilities:
            # Only handle on_off for now
            if cap.type == "devices.capabilities.on_off":
                instance = cap.state.get("instance")
                value = cap.state.get("value")
                # Map value to status
                new_status = "on" if value else "off"
                device_service.device_service.update_device(
                    db=db,
                    device=device,
                    device_in=device_schemas.DeviceUpdate(status=new_status)
                )
                db.refresh(device)

                # Create a command record
                command = device_models.DeviceCommand(
                    device_id=device.id,
                    command_type="open" if new_status == "on" else "close",
                    status="pending"
                )
                db.add(command)
                db.commit()
                db.refresh(command)

                # Publish MQTT message
                topic = f"{current_user.id}/{device.id}/command"
                payload = json.dumps({
                    "command": "open" if new_status == "on" else "close",
                    "command_id": command.id
                })
                mqtt_client.publish(topic, payload)

                device_capabilities.append(device_schemas.DeviceActionCapability(
                    type=cap.type,
                    state={
                        "instance": instance,
                        "action_result": {"status": "DONE"}
                    }
                ))
        response_devices.append(device_schemas.DeviceActionDevice(
            id=str(device.id),
            custom_data={},
            capabilities=device_capabilities
        ))
    return device_schemas.UserDevicesActionResponse(
        payload=device_schemas.UserDevicesActionPayload(devices=response_devices)
    )
 
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

@router.post("/serial-numbers/", response_model=device_schemas.SerialNumberCreateResponse, status_code=status.HTTP_201_CREATED)
async def add_serial_number(
    serial_number_data: device_schemas.SerialNumberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add a single serial number to the database. (Admin only)
    
    The serial number must be in the format SNXXXXXXXXXXXXX (SN followed by 13 digits).
    Example: SN1234567890123
    
    Returns:
    - 201: Serial number successfully created
    - 400: Invalid format or validation error
    - 409: Serial number already exists
    - 403: Insufficient permissions
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    success, message, serial_number_obj = device_service.device_service.add_single_serial_number_to_db(
        db=db, 
        serial_number=serial_number_data.value
    )
    
    if not success:
        # Determine appropriate status code based on error type
        if "Invalid serial number format" in message:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
        elif "already exists" in message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)
    
    return device_schemas.SerialNumberCreateResponse(
        serial_number=device_schemas.SerialNumberRead.model_validate(serial_number_obj, from_attributes=True),
        message=message
    )
