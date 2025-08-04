import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import aiomqtt
from aiomqtt import Client, Message
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class CommandStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class MQTTCommand:
    device_id: str
    command_type: str
    payload: Dict[str, Any]
    correlation_id: str
    timestamp: float
    status: CommandStatus = CommandStatus.PENDING
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class DeviceCommand(BaseModel):
    device_id: str
    command: str
    parameters: Dict[str, Any]
    correlation_id: str
    timestamp: float

class DeviceResponse(BaseModel):
    device_id: str
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    correlation_id: str
    timestamp: float

class MQTTService:
    def __init__(self, broker_host: str, broker_port: int = 1883, username: str = None, password: str = None):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.client: Optional[Client] = None
        self.is_connected = False
        self.pending_commands: Dict[str, MQTTCommand] = {}
        self.response_handlers: Dict[str, Callable] = {}
        self.device_status_callbacks: List[Callable] = []
        
        # MQTT Topics
        self.COMMAND_TOPIC = "devices/+/command"
        self.RESPONSE_TOPIC = "devices/+/response"
        self.STATUS_TOPIC = "devices/+/status"
        self.FEEDBACK_TOPIC = "devices/+/feedback"
        
    async def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client = Client(
                hostname=self.broker_host,
                port=self.broker_port,
                username=self.username,
                password=self.password,
                keepalive=60,
                logger=logger
            )
            
            await self.client.connect()
            self.is_connected = True
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            
            # Start listening for responses and status updates
            asyncio.create_task(self._listen_for_responses())
            asyncio.create_task(self._listen_for_status_updates())
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client and self.is_connected:
            await self.client.disconnect()
            self.is_connected = False
            logger.info("Disconnected from MQTT broker")
    
    async def send_device_command(self, device_id: str, command: str, parameters: Dict[str, Any], timeout: float = 30.0) -> MQTTCommand:
        """Send a command to a specific device and wait for response"""
        if not self.is_connected:
            raise RuntimeError("MQTT client not connected")
        
        import time
        correlation_id = f"cmd_{int(time.time() * 1000)}_{device_id}"
        
        # Create command object
        mqtt_command = MQTTCommand(
            device_id=device_id,
            command_type=command,
            payload=parameters,
            correlation_id=correlation_id,
            timestamp=time.time()
        )
        
        # Store pending command
        self.pending_commands[correlation_id] = mqtt_command
        
        # Prepare message
        command_message = DeviceCommand(
            device_id=device_id,
            command=command,
            parameters=parameters,
            correlation_id=correlation_id,
            timestamp=time.time()
        )
        
        # Send command
        topic = f"devices/{device_id}/command"
        await self.client.publish(
            topic,
            payload=command_message.model_dump_json(),
            qos=1
        )
        
        mqtt_command.status = CommandStatus.SENT
        logger.info(f"Sent command {command} to device {device_id} with correlation_id {correlation_id}")
        
        # Wait for response with timeout
        try:
            await asyncio.wait_for(
                self._wait_for_response(correlation_id),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            mqtt_command.status = CommandStatus.TIMEOUT
            logger.warning(f"Command timeout for device {device_id}, correlation_id {correlation_id}")
        
        return mqtt_command
    
    async def _wait_for_response(self, correlation_id: str):
        """Wait for a specific response"""
        while correlation_id in self.pending_commands:
            command = self.pending_commands[correlation_id]
            if command.status in [CommandStatus.COMPLETED, CommandStatus.FAILED, CommandStatus.TIMEOUT]:
                break
            await asyncio.sleep(0.1)
    
    async def _listen_for_responses(self):
        """Listen for device responses"""
        async with self.client.messages() as messages:
            await self.client.subscribe(self.RESPONSE_TOPIC, qos=1)
            
            async for message in messages:
                try:
                    response_data = json.loads(message.payload.decode())
                    response = DeviceResponse(**response_data)
                    
                    # Find corresponding command
                    if response.correlation_id in self.pending_commands:
                        command = self.pending_commands[response.correlation_id]
                        command.response = response.data
                        command.status = CommandStatus.COMPLETED if response.status == "success" else CommandStatus.FAILED
                        command.error = response.error
                        
                        logger.info(f"Received response for device {response.device_id}, correlation_id {response.correlation_id}")
                        
                        # Call response handler if registered
                        if response.correlation_id in self.response_handlers:
                            handler = self.response_handlers[response.correlation_id]
                            await handler(response)
                    
                except Exception as e:
                    logger.error(f"Error processing device response: {e}")
    
    async def _listen_for_status_updates(self):
        """Listen for device status updates"""
        async with self.client.messages() as messages:
            await self.client.subscribe(self.STATUS_TOPIC, qos=1)
            await self.client.subscribe(self.FEEDBACK_TOPIC, qos=1)
            
            async for message in messages:
                try:
                    status_data = json.loads(message.payload.decode())
                    device_id = message.topic.value.split('/')[1]  # Extract device_id from topic
                    
                    # Notify all status callbacks
                    for callback in self.device_status_callbacks:
                        try:
                            await callback(device_id, status_data)
                        except Exception as e:
                            logger.error(f"Error in status callback: {e}")
                    
                except Exception as e:
                    logger.error(f"Error processing status update: {e}")
    
    def register_status_callback(self, callback: Callable):
        """Register a callback for device status updates"""
        self.device_status_callbacks.append(callback)
    
    def register_response_handler(self, correlation_id: str, handler: Callable):
        """Register a handler for a specific command response"""
        self.response_handlers[correlation_id] = handler
    
    async def get_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a device"""
        if not self.is_connected:
            return None
        
        # Send status request
        await self.client.publish(
            f"devices/{device_id}/status/request",
            payload=json.dumps({"request": "status"}),
            qos=1
        )
        
        # This would need to be implemented with proper response handling
        # For now, return None
        return None
    
    def cleanup_pending_commands(self, max_age: float = 3600):
        """Clean up old pending commands"""
        import time
        current_time = time.time()
        expired_commands = [
            corr_id for corr_id, command in self.pending_commands.items()
            if current_time - command.timestamp > max_age
        ]
        
        for corr_id in expired_commands:
            del self.pending_commands[corr_id]
            if corr_id in self.response_handlers:
                del self.response_handlers[corr_id]

# Global MQTT service instance
mqtt_service: Optional[MQTTService] = None

async def get_mqtt_service() -> MQTTService:
    """Get the global MQTT service instance"""
    global mqtt_service
    if mqtt_service is None:
        raise RuntimeError("MQTT service not initialized")
    return mqtt_service

async def initialize_mqtt_service(broker_host: str, broker_port: int = 1883, username: str = None, password: str = None):
    """Initialize the global MQTT service"""
    global mqtt_service
    mqtt_service = MQTTService(broker_host, broker_port, username, password)
    await mqtt_service.connect()
    return mqtt_service 