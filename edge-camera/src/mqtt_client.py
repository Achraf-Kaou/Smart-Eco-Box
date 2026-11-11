"""
mqtt_client.py – MQTT client for Smart Eco-Box
Publish detection events + Subscribe to feedback commands
"""

import json
import paho.mqtt.client as mqtt
from typing import Optional, Callable
import config


class MQTTClient:
    def __init__(self, on_command: Optional[Callable] = None):
        """
        Args:
            on_command: callback function that will be called
                        when a command is received from the backend
        """
        self.client = mqtt.Client(
            client_id=config.MQTT_CLIENT_ID,
            protocol=mqtt.MQTTv311
        )

        if config.MQTT_USERNAME and config.MQTT_PASSWORD:
            self.client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        self.client.on_message = self._on_message

        self.connected = False
        self.on_command = on_command   # callback for feedback

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"[MQTT] Connected to broker {config.MQTT_BROKER}:{config.MQTT_PORT}")

            # Subscribe to command topic
            client.subscribe(config.MQTT_TOPIC_SUBSCRIBE)
            print(f"[MQTT] Subscribed to topic: {config.MQTT_TOPIC_SUBSCRIBE}")
        else:
            self.connected = False
            print(f"[MQTT] Connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        print("[MQTT] Disconnected from broker")

    def _on_publish(self, client, userdata, mid):
        print(f"[MQTT] Message published (mid={mid})")

    def _on_message(self, client, userdata, msg):
        """Called when a message arrives on the subscribed topic."""
        try:
            payload = json.loads(msg.payload.decode())
            print(f"\n[MQTT] Command received on '{msg.topic}':")
            print(json.dumps(payload, indent=2, ensure_ascii=False))

            # Call the callback if it exists
            if self.on_command:
                self.on_command(payload)

        except Exception as e:
            print(f"[MQTT] Failed to parse command: {e}")

    def connect(self):
        try:
            print(f"[MQTT] Connecting to {config.MQTT_BROKER}...")
            self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            print(f"[MQTT] Connection error: {e}")

    def publish_event(self, event: dict) -> bool:
        if not self.connected:
            print("[MQTT] Not connected – cannot publish")
            return False

        try:
            payload = json.dumps(event, ensure_ascii=False)
            result = self.client.publish(
                topic=config.MQTT_TOPIC_PUBLISH,
                payload=payload,
                qos=1
            )
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"[MQTT] Publish error: {e}")
            return False

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("[MQTT] Client disconnected")