#!/usr/bin/env python3
"""
GPIO Multi-Button MQTT Listener - Version 2
Listens for messages from multiple GPIO buttons
"""

import paho.mqtt.client as mqtt
import json
import time

# MQTT Configuration
MQTT_BROKER = "homeassistant.local"
MQTT_PORT = 1883
MQTT_USERNAME = "iks"
MQTT_PASSWORD = "iks"

# Button topics to listen for
BUTTON_TOPICS = [
    "homeassistant/button/living_room_gpio/state",
    "homeassistant/button/bedroom_gpio/state", 
    "homeassistant/button/kitchen_gpio/state"
]

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to MQTT broker!")
        # Subscribe to all button topics
        for topic in BUTTON_TOPICS:
            client.subscribe(topic)
            print(f"📡 Listening to: {topic}")
        print("Press any GPIO button to see messages...")
    else:
        print(f"❌ Failed to connect: {rc}")

def on_message(client, userdata, msg):
    print(f"\n📨 GPIO Button Message Received:")
    print(f"   Topic: {msg.topic}")
    print(f"   Timestamp: {time.strftime('%H:%M:%S')}")
    try:
        message = json.loads(msg.payload.decode())
        print(f"   Button: {message.get('button_name', 'unknown')}")
        print(f"   Action: {message.get('action', 'unknown')}")
        print(f"   Full JSON: {json.dumps(message, indent=2)}")
    except:
        print(f"   Raw: {msg.payload.decode()}")
    print("─" * 60)

# Create MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

print("🚀 GPIO Multi-Button MQTT Listener v2")
print("=" * 50)

print("Starting listener...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

try:
    print("Press Ctrl+C to stop listening")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 Stopping listener...")
    client.loop_stop()
    client.disconnect()
