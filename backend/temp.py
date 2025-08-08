import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
USERNAME = "mosquitto_user"
PASSWORD = "mosquitto_password"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to MQTT broker!")
        client.subscribe("#")  # Subscribe to all topics on connect
        print("Subscribed to all topics. Waiting for messages...")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("MQTT client is running. Press Ctrl+C to exit.")
client.loop_forever()