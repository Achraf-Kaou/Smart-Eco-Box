"""
config.py – Configuration for Smart Eco-Box
"""

# MQTT Broker settings
# You can use a free public broker for testing, or your HiveMQ / EMQX Cloud instance

MQTT_BROKER = "broker.emqx.io"        # Free public broker (good for testing)
MQTT_PORT = 1883
MQTT_TOPIC_PUBLISH = "smart/waste/detection"
MQTT_TOPIC_SUBSCRIBE = "smart/waste/command"   # for later (feedback)

# Client identity
MQTT_CLIENT_ID = "smart-eco-box-pc-01"

# Optional authentication (leave empty for public brokers)
MQTT_USERNAME = ""
MQTT_PASSWORD = ""