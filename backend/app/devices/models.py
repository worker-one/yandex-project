from datetime import datetime
from sqlalchemy import (
   Column, Integer, String, ForeignKey, Boolean, DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

# Import Base from the central location
from ..models import Base, TimeStampMixin

class SerialNumber(Base, TimeStampMixin):
    """
    Model for managing device serial numbers and their status.
    """
    __tablename__ = 'serial_numbers'

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(15), unique=True, nullable=False, index=True)  # SNXXXXXXXXXXXXX format
    is_free = Column(Boolean, nullable=False, default=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    device_id = Column(Integer, ForeignKey('devices.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    device = relationship(
        "Device",
        back_populates="serial_number_obj",
        primaryjoin="Device.serial_number_id == SerialNumber.id",
        uselist=False
    )

class Device(Base, TimeStampMixin):
    """
    Generic base model for rankable items (Exchanges, Books, etc.).
    Uses joined table inheritance.
    """
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True, index=True)
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    status = Column(String(50), nullable=False, default='off')  # 'on' or 'off'
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    type = Column(String(50), nullable=False, default='openable')
    room = Column(String(100), nullable=True, default=None)

    # relationship fields
    owner = relationship(
        "User", 
        back_populates="devices",
        foreign_keys=[user_id]
    )
    serial_number_obj = relationship(
        "SerialNumber",
        back_populates="device",
        foreign_keys=[serial_number_id],
        uselist=False
    )

    @hybrid_property
    def serial_number(self):
        """Get the serial number string from the related SerialNumber object."""
        return self.serial_number_obj.value if self.serial_number_obj else None


# Device status tracking
class DeviceStatus(Base):
    __tablename__ = "device_statuses"
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    is_online = Column(Boolean, default=False)
    battery_level = Column(Integer, nullable=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
# Command history
class DeviceCommand(Base):
    __tablename__ = "device_commands"
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    command_type = Column(String)  # "open", "close"
    status = Column(String)  # "pending", "success", "error"
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

# Device events
class DeviceEvent(Base):
    __tablename__ = "device_events"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    event_type = Column(String) # "warning", "error"
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)