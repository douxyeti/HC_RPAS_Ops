import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
SESSION_TOPIC = "hc_rpas/sso/sessions"

def clear_topic():
    """Connects to MQTT and clears the retained message on the session topic."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, f"sso_cleanup_client_{int(time.time())}")
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
            print(f"Clearing topic: {SESSION_TOPIC}")
            client.publish(SESSION_TOPIC, payload="", qos=1, retain=True)
        else:
            print(f"Failed to connect, return code {rc}\n")
            client.loop_stop() # Stop the loop on connection failure

    def on_publish(client, userdata, mid, reason_code, properties):
        """Callback for when a message is published."""
        print("Topic cleared successfully.")
        client.disconnect() # This will cause loop_forever() to exit

    def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
        print("Disconnected from MQTT Broker.")

    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        # loop_forever() is a blocking call that processes network traffic,
        # dispatches callbacks and handles reconnecting.
        # It will exit when disconnect() is called.
        client.loop_forever()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    clear_topic()
