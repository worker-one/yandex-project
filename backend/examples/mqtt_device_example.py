#!/usr/bin/env python3
"""
Example MQTT device implementation.
This shows how a physical device should implement MQTT communication
to receive commands from the Yandex Smart Home backend.
"""

import asyncio
import json
import logging
from typing import Dict, Any
import aiomqtt
from aiomqtt import Client
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExampleDevice:
    """Example device that communicates via MQTT"""
    
    def __init__(self, device_id: str, broker_host: str = "localhost", broker_port: int = 1883):
        self.device_id = device_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client: Client = None
        self.is_connected = False
        
        # Device state
        self.power = False
        self.temperature = 25.0
        self.mode = "normal"
        
        # MQTT Topics
        self.command_topic = f"devices/{device_id}/command"
        self.response_topic = f"devices/{device_id}/response"
        self.status_topic = f"devices/{device_id}/status"
        self.feedback_topic = f"devices/{device_id}/feedback"
    
    async def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client = Client(
                hostname=self.broker_host,
                port=self.broker_port,
                keepalive=60,
                logger=logger
            )
            
            await self.client.connect()
            self.is_connected = True
            logger.info(f"Device {self.device_id} connected to MQTT broker")
            
            # Start listening for commands
            asyncio.create_task(self._listen_for_commands())
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client and self.is_connected:
            await self.client.disconnect()
            self.is_connected = False
            logger.info(f"Device {self.device_id} disconnected from MQTT broker")
    
    async def _listen_for_commands(self):
        """Listen for incoming commands"""
        async with self.client.messages() as messages:
            await self.client.subscribe(self.command_topic, qos=1)
            
            async for message in messages:
                try:
                    command_data = json.loads(message.payload.decode())
                    await self._handle_command(command_data)
                except Exception as e:
                    logger.error(f"Error processing command: {e}")
    
    async def _handle_command(self, command_data: Dict[str, Any]):
        """Handle incoming command"""
        command = command_data.get("command")
        parameters = command_data.get("parameters", {})
        correlation_id = command_data.get("correlation_id")
        
        logger.info(f"Received command: {command} with parameters: {parameters}")
        
        try:
            if command == "set_power":
                await self._handle_set_power(parameters, correlation_id)
            elif command == "set_range":
                await self._handle_set_range(parameters, correlation_id)
            elif command == "set_mode":
                await self._handle_set_mode(parameters, correlation_id)
            else:
                await self._send_error_response(correlation_id, f"Unknown command: {command}")
                
        except Exception as e:
            logger.error(f"Error handling command {command}: {e}")
            await self._send_error_response(correlation_id, str(e))
    
    async def _handle_set_power(self, parameters: Dict[str, Any], correlation_id: str):
        """Handle power on/off command"""
        power = parameters.get("power", False)
        
        # Simulate device operation
        logger.info(f"Setting power to: {power}")
        self.power = power
        
        # Simulate some processing time
        await asyncio.sleep(0.5)
        
        # Send success response
        await self._send_success_response(correlation_id, {"power": self.power})
        
        # Publish status update
        await self._publish_status()
    
    async def _handle_set_range(self, parameters: Dict[str, Any], correlation_id: str):
        """Handle range setting command (e.g., temperature)"""
        instance = parameters.get("instance")
        value = parameters.get("value")
        
        if instance == "temperature":
            logger.info(f"Setting temperature to: {value}")
            self.temperature = float(value)
            
            # Simulate some processing time
            await asyncio.sleep(1.0)
            
            # Send success response
            await self._send_success_response(correlation_id, {"temperature": self.temperature})
            
            # Publish status update
            await self._publish_status()
        else:
            await self._send_error_response(correlation_id, f"Unknown range instance: {instance}")
    
    async def _handle_set_mode(self, parameters: Dict[str, Any], correlation_id: str):
        """Handle mode setting command"""
        mode = parameters.get("mode", "normal")
        
        logger.info(f"Setting mode to: {mode}")
        self.mode = mode
        
        # Simulate some processing time
        await asyncio.sleep(0.3)
        
        # Send success response
        await self._send_success_response(correlation_id, {"mode": self.mode})
        
        # Publish status update
        await self._publish_status()
    
    async def _send_success_response(self, correlation_id: str, data: Dict[str, Any]):
        """Send successful command response"""
        response = {
            "device_id": self.device_id,
            "status": "success",
            "data": data,
            "correlation_id": correlation_id,
            "timestamp": time.time()
        }
        
        await self.client.publish(
            self.response_topic,
            payload=json.dumps(response),
            qos=1
        )
        
        logger.info(f"Sent success response for correlation_id: {correlation_id}")
    
    async def _send_error_response(self, correlation_id: str, error: str):
        """Send error response"""
        response = {
            "device_id": self.device_id,
            "status": "error",
            "error": error,
            "correlation_id": correlation_id,
            "timestamp": time.time()
        }
        
        await self.client.publish(
            self.response_topic,
            payload=json.dumps(response),
            qos=1
        )
        
        logger.error(f"Sent error response for correlation_id {correlation_id}: {error}")
    
    async def _publish_status(self):
        """Publish current device status"""
        status = {
            "power": self.power,
            "temperature": self.temperature,
            "mode": self.mode,
            "timestamp": time.time()
        }
        
        await self.client.publish(
            self.status_topic,
            payload=json.dumps(status),
            qos=1
        )
        
        logger.debug(f"Published status: {status}")
    
    async def publish_feedback(self, feedback_type: str, data: Dict[str, Any]):
        """Publish device feedback (e.g., sensor readings, alerts)"""
        feedback = {
            "type": feedback_type,
            "data": data,
            "timestamp": time.time()
        }
        
        await self.client.publish(
            self.feedback_topic,
            payload=json.dumps(feedback),
            qos=1
        )
        
        logger.info(f"Published feedback: {feedback}")
    
    async def run(self):
        """Main device loop"""
        await self.connect()
        
        try:
            # Publish initial status
            await self._publish_status()
            
            # Main device loop
            while self.is_connected:
                # Simulate periodic operations
                if self.power:
                    # Simulate temperature changes when powered on
                    if self.temperature < 100:
                        self.temperature += 0.1
                    
                    # Publish feedback every 10 seconds
                    if int(time.time()) % 10 == 0:
                        await self.publish_feedback("sensor_reading", {
                            "temperature": self.temperature,
                            "power_consumption": 150.5
                        })
                
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Device shutdown requested")
        finally:
            await self.disconnect()


async def main():
    """Main function to run the example device"""
    # Create device instance
    device = ExampleDevice(
        device_id="kettle-12345",  # This should match the device ID in your database
        broker_host="localhost",
        broker_port=1883
    )
    
    # Run the device
    await device.run()


if __name__ == "__main__":
    asyncio.run(main()) 