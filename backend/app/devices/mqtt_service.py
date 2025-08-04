import asyncio
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.devices import models as device_models
from app.devices import schemas as device_schemas
from app.mqtt.service import get_mqtt_service, MQTTCommand, CommandStatus
from app.config import settings

logger = logging.getLogger(__name__)

class DeviceMQTTService:
    """Service for handling device commands via MQTT"""
    
    def __init__(self):
        self.device_status_cache: Dict[str, Dict[str, Any]] = {}
    
    async def send_device_command(
        self, 
        db: Session, 
        device: device_models.Device, 
        command_type: str, 
        parameters: Dict[str, Any]
    ) -> MQTTCommand:
        """Send a command to a device via MQTT"""
        try:
            mqtt_service = await get_mqtt_service()
            
            # Use device serial number as MQTT device ID
            device_id = device.serial_number
            
            # Send command via MQTT
            mqtt_command = await mqtt_service.send_device_command(
                device_id=device_id,
                command=command_type,
                parameters=parameters,
                timeout=settings.MQTT_COMMAND_TIMEOUT
            )
            
            logger.info(f"Sent MQTT command {command_type} to device {device_id}")
            return mqtt_command
            
        except Exception as e:
            logger.error(f"Failed to send MQTT command to device {device.id}: {e}")
            raise
    
    async def handle_yandex_command(
        self, 
        db: Session, 
        device: device_models.Device, 
        capability_type: str, 
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle Yandex Smart Home commands and translate to MQTT"""
        
        # Map Yandex capabilities to MQTT commands
        command_mapping = {
            "devices.capabilities.on_off": {
                "command": "set_power",
                "parameter_key": "value"
            },
            "devices.capabilities.range": {
                "command": "set_range",
                "parameter_key": "instance"
            },
            "devices.capabilities.mode": {
                "command": "set_mode",
                "parameter_key": "instance"
            },
            "devices.capabilities.toggle": {
                "command": "set_toggle",
                "parameter_key": "instance"
            }
        }
        
        if capability_type not in command_mapping:
            raise ValueError(f"Unsupported capability type: {capability_type}")
        
        mapping = command_mapping[capability_type]
        command = mapping["command"]
        parameter_key = mapping["parameter_key"]
        
        # Extract parameters based on capability type
        if capability_type == "devices.capabilities.on_off":
            parameters = {
                "power": state.get("value", False)
            }
        elif capability_type == "devices.capabilities.range":
            instance = state.get("instance")
            value = state.get("value")
            parameters = {
                "instance": instance,
                "value": value
            }
        else:
            # For other capabilities, pass the state as-is
            parameters = state
        
        # Send command via MQTT
        mqtt_command = await self.send_device_command(
            db=db,
            device=device,
            command_type=command,
            parameters=parameters
        )
        
        # Return response based on MQTT command status
        if mqtt_command.status == CommandStatus.COMPLETED:
            return {
                "status": "DONE",
                "data": mqtt_command.response
            }
        elif mqtt_command.status == CommandStatus.FAILED:
            return {
                "status": "ERROR",
                "error": mqtt_command.error or "Command failed"
            }
        elif mqtt_command.status == CommandStatus.TIMEOUT:
            return {
                "status": "ERROR",
                "error": "Command timeout"
            }
        else:
            return {
                "status": "ERROR",
                "error": f"Unexpected status: {mqtt_command.status}"
            }
    
    async def get_device_status_from_mqtt(self, device: device_models.Device) -> Optional[Dict[str, Any]]:
        """Get device status from MQTT cache or request from device"""
        device_id = device.serial_number
        
        # Check cache first
        if device_id in self.device_status_cache:
            return self.device_status_cache[device_id]
        
        # Request status from device via MQTT
        try:
            mqtt_service = await get_mqtt_service()
            status = await mqtt_service.get_device_status(device_id)
            if status:
                self.device_status_cache[device_id] = status
            return status
        except Exception as e:
            logger.error(f"Failed to get device status from MQTT for device {device_id}: {e}")
            return None
    
    def update_device_status_cache(self, device_id: str, status_data: Dict[str, Any]):
        """Update device status cache with new data"""
        self.device_status_cache[device_id] = status_data
        logger.debug(f"Updated status cache for device {device_id}: {status_data}")
    
    async def register_device_status_callback(self):
        """Register callback to handle device status updates"""
        try:
            mqtt_service = await get_mqtt_service()
            mqtt_service.register_status_callback(self._handle_device_status_update)
            logger.info("Registered device status callback")
        except Exception as e:
            logger.error(f"Failed to register device status callback: {e}")
    
    async def _handle_device_status_update(self, device_id: str, status_data: Dict[str, Any]):
        """Handle device status updates from MQTT"""
        # Update cache
        self.update_device_status_cache(device_id, status_data)
        
        # Here you could also update the database or trigger other actions
        # For example, notify connected clients via WebSocket
        logger.info(f"Device {device_id} status updated: {status_data}")
    
    def get_cached_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device status from cache"""
        return self.device_status_cache.get(device_id)
    
    def clear_device_status_cache(self, device_id: str = None):
        """Clear device status cache"""
        if device_id:
            self.device_status_cache.pop(device_id, None)
        else:
            self.device_status_cache.clear()

# Global instance
device_mqtt_service = DeviceMQTTService() 