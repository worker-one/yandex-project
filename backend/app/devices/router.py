# app/item/router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload # Changed AsyncSession to Session

from app.database.core import get_db
from app.devices import schemas as item_schemas
from app.devices import service as item_service
from app.dependencies import get_current_active_user
from app.auth.models import User
from app.devices.models import Item  # add this import

router = APIRouter(
    tags=["Devices"]
)


@router.get("/{device_serial_number}", response_model=item_schemas.DeviceRead)
async def get_device(
    device_serial_number: str,
    db: Session = Depends(get_db) # Changed AsyncSession to Session
):
    """
    Get a specific device by its serial number.
    """
    device = item_service.item_service.get_device_by_serial_number(db=db, device_serial_number=device_serial_number, options=[selectinload(Item.owner)]) # Removed await
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device

@router.put("/{device_serial_number}", response_model=item_schemas.DeviceRead)
async def update_device(
    device_serial_number: str,
    device_in: item_schemas.DeviceUpdate,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a device.
    """
    device = item_service.item_service.get_device_by_serial_number(db=db, device_serial_number=device_serial_number, options=[selectinload(Item.owner)])
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if device.user_id != current_user.id and not current_user.is_superuser: # Changed item.owner_id to item.user_id
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    updated_device = item_service.item_service.update_device(db=db, device=device, device_in=device_in)
    db.refresh(updated_device, attribute_names=["owner"])
    return updated_device

@router.delete("/{device_serial_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_serial_number: str,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a device.
    """
    device = item_service.item_service.get_device_by_serial_number(db=db, device_serial_number=device_serial_number, options=[selectinload(Item.owner)])
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if device.user_id != current_user.id and not current_user.is_superuser: # Changed item.owner_id to item.user_id
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    item_service.item_service.delete_device(db=db, device=device)
    return None


@router.get("/", response_model=item_schemas.DeviceListResponse)
async def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    name: str = Query(None),
    user_id: int = Query(None), # Changed owner_id to user_id
    sort_field: str = Query("id"),
    sort_direction: str = Query("asc"),
    db: Session = Depends(get_db)
):
    """
    List devices with filtering, sorting, and pagination.
    """
    filters = item_schemas.DeviceFilter(
        name=name,
        user_id=user_id # Changed owner_id to user_id
    )
    sort = item_schemas.DeviceSort(
        field=sort_field,
        direction=sort_direction
    )
    devices = item_service.item_service.list_devices(  # Removed await
        db=db,
        skip=skip,
        limit=limit,
        filters=filters,
        sort=sort,
        options=[selectinload(Item.owner)]
    )
    return devices

@router.post("/", response_model=item_schemas.DeviceRead, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_in: item_schemas.DeviceCreate,
    db: Session = Depends(get_db), # Changed AsyncSession to Session
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new device.
    """
    device = item_service.item_service.create_device(db=db, device_in=device_in, owner_id=current_user.id) # Removed await
    db.refresh(device, attribute_names=["owner"]) # Removed await
    return device

# Get user's devices list
# GET https://example.com/v1.0/user/devices
@router.get("/user/devices", response_model=item_schemas.DevicesListResponse)
async def get_user_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's devices with pagination.
    """
    devices = item_service.item_service.get_user_devices(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        options=[selectinload(Item.owner)]
    )
    return devices

# Get user's devices status with query parameters
# POST https://example.com/v1.0/user/devices/query
@router.post("/user/devices/query", response_model=item_schemas.DevicesListResponse)
async def query_user_devices(
    query: item_schemas.DeviceQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Query user's devices with filters.
    """
    devices = item_service.item_service.query_user_devices(db=db, user_id=current_user.id, filters=query)
    return devices