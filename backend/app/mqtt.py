import paho.mqtt.client as mqtt
from app.config import settings
import logging
import time
import json
from app.database.core import SessionFactory
from app.devices.models import DeviceStatus, DeviceCommand, DeviceEvent
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        self.connected = False

    def connect(self):
        retries = 10
        for i in range(retries):
            try:
                logger.info(f"Attempting to connect to MQTT broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT} (attempt {i+1}/{retries})")
                self.client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
                self.client.loop_start()
                time.sleep(2)
                if self.connected:
                    logger.info("MQTT client connected successfully.")
                    return
            except Exception as e:
                logger.error(f"Failed to connect to MQTT broker: {e}. Retrying in 10 seconds...")
                time.sleep(10)
        logger.error("Failed to connect to MQTT broker after several retries.")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
            self.connected = True
            client.subscribe("+/+/info")
            client.subscribe("+/+/warning")
            client.subscribe("+/+/error")
            client.subscribe("+/+/command/response")
        else:
            logger.error(f"Failed to connect, return code {rc}")
            self.connected = False

    def on_message(self, client, userdata, msg):
        logger.info(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
        try:
            topic_parts = msg.topic.split('/')
            if len(topic_parts) < 3:
                logger.warning(f"Invalid topic format: {msg.topic}")
                return

            user_id, device_id, sub_topic = topic_parts[0], topic_parts[1], topic_parts[2]
            payload = json.loads(msg.payload.decode())

            with SessionFactory() as db_session:
                if sub_topic == "info":
                    self.handle_info(db_session, device_id, payload)
                elif sub_topic == "warning":
                    self.handle_warning(db_session, device_id, payload)
                elif sub_topic == "error":
                    self.handle_error(db_session, device_id, payload)
                elif sub_topic == "command" and len(topic_parts) > 3 and topic_parts[3] == "response":
                    self.handle_command_response(db_session, device_id, payload)

        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON payload: {msg.payload.decode()}")
        except Exception as e:
            logger.error(f"Error processing message on topic {msg.topic}: {e}")

    def handle_info(self, db, device_id, payload):
        status = db.query(DeviceStatus).filter(DeviceStatus.device_id == device_id).first()
        if not status:
            status = DeviceStatus(device_id=device_id)
            db.add(status)
        
        status.is_online = payload.get("status") == "online"
        status.battery_level = payload.get("battery_level")
        status.last_seen = datetime.utcnow()
        db.commit()

    def handle_warning(self, db, device_id, payload):
        event = DeviceEvent(
            device_id=device_id,
            event_type="warning",
            message=payload.get("message")
        )
        db.add(event)
        db.commit()

    def handle_error(self, db, device_id, payload):
        event = DeviceEvent(
            device_id=device_id,
            event_type="error",
            message=payload.get("message")
        )
        db.add(event)
        db.commit()

    def handle_command_response(self, db, device_id, payload):
        command_id = payload.get("command_id")
        command = db.query(DeviceCommand).filter(DeviceCommand.id == command_id).first()
        if command:
            command.status = payload.get("status")
            command.completed_at = datetime.utcnow()
            db.commit()

    def publish(self, topic, payload, qos=1):
        try:
            self.client.publish(topic, payload, qos)
            logger.info(f"Published message to topic {topic}: {payload}")
        except Exception as e:
            logger.error(f"Failed to publish message to topic {topic}: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        logger.info("MQTT client disconnected.")

mqtt_client = MQTTClient()
