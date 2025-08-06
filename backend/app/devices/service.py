# app/item/service.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, asc, desc, func
from typing import Optional, List
import logging
import re

from app.devices import models as device_models
from app.devices import schemas as device_schemas

# Get logger
logger = logging.getLogger(__name__)

class DeviceService:
    def get_device_by_id(self, db: Session, device_id: int, options: List = None) -> Optional[device_models.Device]:
        """Retrieve a single device by its ID."""
        logger.info(f"Retrieving device with id {device_id}.")
        query = select(device_models.Device).filter(device_models.Device.id == device_id)
        if options:
            for option in options:
                query = query.options(option)
        device = db.execute(query).scalars().first()
        logger.info(f"Device with id {device_id} {'found' if device else 'not found'}.")
        return device

    def get_device_by_serial_number(self, db: Session, device_serial_number: str, options: List = None) -> Optional[device_models.Device]:
        """Retrieve a single device by its serial number."""
        logger.info(f"Retrieving device with serial number {device_serial_number}.")
        
        query = select(device_models.Device).join(device_models.SerialNumber).filter(device_models.SerialNumber.value == device_serial_number)
        if options:
            for option in options:
                query = query.options(option)
        device = db.execute(query).scalars().first()
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

        if options:
            for option in options:
                query = query.options(option)

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

        devices_read = [device_schemas.DeviceRead.model_validate(device, from_attributes=True) for device in devices]

        return device_schemas.DeviceListResponse(
            devices=devices_read,
            total=total
        )

    def validate_serial_number_format(self, serial_number: str) -> bool:
        """Validate serial number format SNXXXXXXXXXXXXX (SN + 13 digits)."""
        pattern = r'^SN\d{13}$'
        return bool(re.match(pattern, serial_number))

    def add_serial_numbers_to_db(self, db: Session, serial_numbers: List[str]) -> List[device_models.SerialNumber]:
        """Add multiple serial numbers to the database."""
        logger.info(f"Adding {len(serial_numbers)} serial numbers to database.")
        created_serial_numbers = []
        
        for sn in serial_numbers:
            if not self.validate_serial_number_format(sn):
                logger.warning(f"Invalid serial number format: {sn}. Expected format: SNXXXXXXXXXXXXX (SN followed by 13 digits)")
                continue
                
            existing = db.execute(select(device_models.SerialNumber).filter(device_models.SerialNumber.value == sn)).scalars().first()
            
            if existing:
                logger.warning(f"Serial number {sn} already exists in database.")
                continue
                
            serial_number_obj = device_models.SerialNumber(value=sn)
            db.add(serial_number_obj)
            created_serial_numbers.append(serial_number_obj)
        
        db.commit()
        logger.info(f"Successfully added {len(created_serial_numbers)} serial numbers.")
        return created_serial_numbers

    def get_all_serial_numbers(self, db: Session, skip: int = 0, limit: int = 100) -> dict:
        """Get all serial numbers with their status."""
        logger.info("Retrieving all serial numbers from database.")
        
        total_query = select(func.count(device_models.SerialNumber.id))
        total = db.scalar(total_query)
        
        query = select(device_models.SerialNumber).offset(skip).limit(limit)
        result = db.execute(query)
        serial_numbers = result.scalars().all()
        
        return {
            'serial_numbers': serial_numbers,
            'total': total
        }

    def check_serial_number_availability(self, db: Session, serial_number: str) -> tuple[bool, Optional[device_models.SerialNumber]]:
        """Check if serial number exists and is free."""
        sn_obj = db.execute(select(device_models.SerialNumber).filter(device_models.SerialNumber.value == serial_number)).scalars().first()
        
        if not sn_obj:
            return False, None
        
        return sn_obj.is_free, sn_obj

    def bind_serial_number(self, db: Session, serial_number: str, user_id: int, device_id: int) -> bool:
        """Bind serial number to user and device."""
        logger.info(f"Binding serial number {serial_number} to user {user_id} and device {device_id}.")
        
        sn_obj = db.execute(select(device_models.SerialNumber).filter(device_models.SerialNumber.value == serial_number)).scalars().first()
        
        if not sn_obj or not sn_obj.is_free:
            logger.warning(f"Serial number {serial_number} not available for binding.")
            return False
        
        sn_obj.is_free = False
        sn_obj.user_id = user_id
        sn_obj.device_id = device_id
        db.commit()
        
        logger.info(f"Successfully bound serial number {serial_number}.")
        return True

    def unbind_serial_number(self, db: Session, serial_number: str) -> bool:
        """Unbind serial number and mark as free."""
        logger.info(f"Unbinding serial number {serial_number}.")
        
        sn_obj = db.execute(select(device_models.SerialNumber).filter(device_models.SerialNumber.value == serial_number)).scalars().first()
        
        if not sn_obj:
            logger.warning(f"Serial number {serial_number} not found.")
            return False
        
        sn_obj.is_free = True
        sn_obj.user_id = None
        sn_obj.device_id = None
        db.commit()
        
        logger.info(f"Successfully unbound serial number {serial_number}.")
        return True

    def create_device(self, db: Session, device_in: device_schemas.DeviceCreate, owner_id: int) -> device_models.Device:
        """Create a new device with serial number validation."""
        if not self.validate_serial_number_format(device_in.serial_number):
            raise ValueError(f"Invalid serial number format: {device_in.serial_number}. Expected format: SNXXXXXXXXXXXXX (SN followed by 13 digits)")
        
        is_available, sn_obj = self.check_serial_number_availability(db, device_in.serial_number)
        if not is_available:
            if sn_obj is None:
                raise ValueError(f"Serial number {device_in.serial_number} not found in database")
            else:
                raise ValueError(f"Serial number {device_in.serial_number} is already in use")
        
        try:
            device_data = device_in.model_dump(exclude={'serial_number'})
            device_data['user_id'] = owner_id
            device_data['serial_number_id'] = sn_obj.id

            device = device_models.Device(**device_data)
            db.add(device)
            db.flush()
            
            sn_obj.is_free = False
            sn_obj.user_id = owner_id
            sn_obj.device_id = device.id
            
            db.commit()
            db.refresh(device)
            
            logger.info(f"Successfully created device {device.id} with serial number {device_in.serial_number}")
            return device
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create device with serial number {device_in.serial_number}: {str(e)}")
            raise ValueError(f"Failed to create device: {str(e)}")

    def update_device(self, db: Session, device: device_models.Device, device_in: device_schemas.DeviceUpdate) -> device_models.Device:
        """Update an existing device."""
        update_data = device_in.model_dump(exclude_unset=True)
        
        try:
            if 'serial_number' in update_data and update_data['serial_number'] != device.serial_number:
                new_sn_value = update_data['serial_number']
                
                if not self.validate_serial_number_format(new_sn_value):
                    raise ValueError(f"Invalid serial number format: {new_sn_value}.")

                is_available, new_sn_obj = self.check_serial_number_availability(db, new_sn_value)
                if not is_available:
                    raise ValueError(f"Serial number {new_sn_value} is not available.")

                # Unbind old serial number
                if device.serial_number_obj:
                    device.serial_number_obj.is_free = True
                    device.serial_number_obj.user_id = None
                    device.serial_number_obj.device_id = None

                # Bind new serial number
                new_sn_obj.is_free = False
                new_sn_obj.user_id = device.user_id
                new_sn_obj.device_id = device.id
                device.serial_number_id = new_sn_obj.id
                device.serial_number_obj = new_sn_obj

            for field, value in update_data.items():
                if field != 'serial_number':
                    setattr(device, field, value)
            
            db.commit()
            db.refresh(device)
            db.refresh(device.serial_number_obj)

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update device {device.id}: {str(e)}")
            raise
            
        return device

    def delete_device(self, db: Session, device: device_models.Device) -> None:
        """Delete a device and unbind its serial number."""
        serial_number = device.serial_number
        
        if serial_number:
            self.unbind_serial_number(db, serial_number)
        
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
        if options:
            for option in options:
                query = query.options(option)
        
        total_query = select(func.count(device_models.Device.id)).where(device_models.Device.user_id == user_id)
        total = db.scalar(total_query)
        
        query = query.offset(skip).limit(limit)
        result = db.execute(query)
        devices = result.scalars().all()
        
        if return_orm:
            return type('DevicesResult', (), {'devices': devices, 'total': total})()
        
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

    def add_single_serial_number_to_db(self, db: Session, serial_number: str) -> tuple[bool, str, device_models.SerialNumber]:
        """
        Add a single serial number to the database.
        Returns: (success: bool, message: str, serial_number_obj: SerialNumber or None)
        """
        logger.info(f"Adding serial number {serial_number} to database.")
        
        if not self.validate_serial_number_format(serial_number):
            error_msg = f"Invalid serial number format: {serial_number}. Expected format: SNXXXXXXXXXXXXX (SN followed by 13 digits)"
            logger.warning(error_msg)
            return False, error_msg, None
        
        existing = db.execute(select(device_models.SerialNumber).filter(device_models.SerialNumber.value == serial_number)).scalars().first()
        
        if existing:
            error_msg = f"Serial number {serial_number} already exists in database"
            logger.warning(error_msg)
            return False, error_msg, None
        
        try:
            serial_number_obj = device_models.SerialNumber(value=serial_number)
            db.add(serial_number_obj)
            db.commit()
            db.refresh(serial_number_obj)
            
            success_msg = f"Serial number {serial_number} successfully added to database"
            logger.info(success_msg)
            return True, success_msg, serial_number_obj
            
        except Exception as e:
            db.rollback()
            error_msg = f"Failed to add serial number {serial_number}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None

device_service = DeviceService()