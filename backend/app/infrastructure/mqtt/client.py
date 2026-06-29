import paho.mqtt.client as mqtt

from app.core.config import settings


def build_mqtt_client(client_id: str = "ultralink-monitor-api") -> mqtt.Client:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    if settings.mqtt_username:
        client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
    return client
