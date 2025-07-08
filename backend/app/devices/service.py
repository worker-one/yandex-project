# app/item/service.py
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc, func
from typing import Optional, List
import logging

from app.devices import models as device_models
from app.devices import schemas as device_schemas

# Get logger
logger = logging.getLogger(__name__)

class DeviceService:
    def get_device_by_id(self, db: Session, device_id: int, options: List = None) -> Optional[device_models.Device]:
        """Retrieve a single device by its ID."""
        logger.info(f"Retrieving device with id {device_id}.")
        query = db.query(device_models.Device)
        if options:
            query = query.options(*options)
        device = query.filter(device_models.Device.id == device_id).first()
        logger.info(f"Device with id {device_id} {'found' if device else 'not found'}.")
        return device

    def get_device_by_serial_number(self, db: Session, device_serial_number: str, options: List = None) -> Optional[device_models.Device]:
        """Retrieve a single device by its serial number."""
        logger.info(f"Retrieving device with serial number {device_serial_number}.")
        query = db.query(device_models.Device)
        if options:
            query = query.options(*options)
        device = query.filter(device_models.Device.serial_number == device_serial_number).first()
        logger.info(f"Device with serial number {device_serial_number} {'found' if device else 'not found'}.")
        return device

    def list_devices(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: device_schemas.DeviceFilter = None,
        sort: device_schemas.DeviceSort = None,
        options: List = None
    ):
        """
        Retrieve a list of devices with optional filtering, sorting, and pagination.
        """
        query = select(device_models.Device)

        # Filtering
        if filters:
            if filters.name is not None:
                query = query.where(device_models.Device.name.ilike(f"%{filters.name}%"))
            if filters.user_id is not None:
                query = query.where(device_models.Device.user_id == filters.user_id)

        # Sorting
        if sort:
            sort_field = getattr(device_models.Device, sort.field, None)
            if sort_field is not None:
                if sort.direction == "desc":
                    query = query.order_by(desc(sort_field))
                else:
                    query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(asc(device_models.Device.id))

        query = query.options(*(options or []))

        # Count total
        total_query = select(func.count(device_models.Device.id))
        if filters:
            if filters.name is not None:
                total_query = total_query.where(device_models.Device.name.ilike(f"%{filters.name}%"))
            if filters.user_id is not None:
                total_query = total_query.where(device_models.Device.user_id == filters.user_id)
        
        total = db.scalar(total_query)

        # Pagination
        query = query.offset(skip).limit(limit)
        result = db.execute(query)
        devices = result.scalars().all()

        # Convert SQLAlchemy models to Pydantic models
        devices_read = []
        for device in devices:
            device_read = device_schemas.DeviceRead.model_validate(device, from_attributes=True)
            device_read.custom_data["serial_number"] = device.serial_number
            devices_read.append(device_read)

        return device_schemas.DeviceListResponse(
            devices=devices_read,
            total=total
        )

    def create_device(self, db: Session, device_in: device_schemas.DeviceCreate, owner_id: int) -> device_models.Device:
        """Create a new device."""
        device_data = device_in.model_dump()
        device_data['user_id'] = owner_id

        device = device_models.Device(**device_data)
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

    def update_device(self, db: Session, device: device_models.Device, device_in: device_schemas.DeviceUpdate) -> device_models.Device:
        """Update an existing device."""
        for field, value in device_in.model_dump(exclude_unset=True).items():
            setattr(device, field, value)
        db.commit()
        db.refresh(device)
        return device

    def delete_device(self, db: Session, device: device_models.Device) -> None:
        """Delete a device."""
        db.delete(device)
        db.commit()

    def get_user_devices(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        options: List = None,
        return_orm: bool = False
    ):
        """Get devices for a specific user."""
        query = select(device_models.Device).where(device_models.Device.user_id == user_id)
        query = query.options(*(options or []))
        
        total_query = select(func.count(device_models.Device.id)).where(device_models.Device.user_id == user_id)
        total = db.scalar(total_query)
        
        query = query.offset(skip).limit(limit)
        result = db.execute(query)
        devices = result.scalars().all()
        
        if return_orm:
            # Return raw ORM instances for updates
            return type('DevicesResult', (), {
                'devices': devices,
                'total': total
            })()
        
        devices_read = [device_schemas.DeviceRead.model_validate(device, from_attributes=True) for device in devices]
        
        return device_schemas.DevicesListResponse(
            devices=devices_read,
            total=total
        )

    def query_user_devices(self, db: Session, user_id: int, filters: device_schemas.DeviceQuery):
        """Query user devices with filters."""
        query = select(device_models.Device).where(device_models.Device.user_id == user_id)
        
        if filters.name:
            query = query.where(device_models.Device.name.ilike(f"%{filters.name}%"))
        
        result = db.execute(query)
        devices = result.scalars().all()
        
        devices_read = [device_schemas.DeviceRead.model_validate(device, from_attributes=True) for device in devices]
        
        return device_schemas.DevicesListResponse(
            devices=devices_read,
            total=len(devices_read)
        )

device_service = DeviceService()