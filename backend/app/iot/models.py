from sqlalchemy import (
    Boolean, Column, Integer, String, Text, ForeignKey, DateTime, JSON
)
from sqlalchemy.orm import relationship

# Import Base from the central location
from ..models import Base, TimeStampMixin

class Device(Base, TimeStampMixin):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    room = Column(String(100))
    type = Column(String(100), nullable=False)

    device_info = relationship("DeviceInfo", back_populates="device", uselist=False, cascade="all, delete-orphan")
    capabilities = relationship("Capability", back_populates="device", cascade="all, delete-orphan")


class DeviceInfo(Base, TimeStampMixin):
    __tablename__ = 'device_infos'

    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String(100))
    model = Column(String(100))
    hw_version = Column(String(50))
    sw_version = Column(String(50))
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False, unique=True)

    device = relationship("Device", back_populates="device_info")


class Capability(Base, TimeStampMixin):
    __tablename__ = 'capabilities'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100), nullable=False)
    retrievable = Column(Boolean, default=True)
    reportable = Column(Boolean, default=True)
    parameters = Column(JSON)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False)

    device = relationship("Device", back_populates="capabilities")