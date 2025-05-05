import json
import threading
import paho.mqtt.client as mqtt
from config import Settings
from predictor import FailurePredictor
from email_alerts import alert_sensor, report_failure
from history import save_record, init_history

settings = Settings()
init_history()
predictor = FailurePredictor(
    str(settings.model_path), settings.sequence_length, settings.input_features
)

esp_data = {key: {"history": [], "status": "OK"} for key in settings.topics}


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        for topic in settings.topics.values():
            client.subscribe(topic)


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    esp_id = [k for k, v in settings.topics.items() if v == msg.topic][0]
    data = {
        "temperature": payload.get("temperature"),
        "humidity": payload.get("humidity"),
        "vibration": payload.get("vibration"),
        "voltage": payload.get("voltage"),
        "current": payload.get("current"),
        "alerts": [],
    }
    esp_data[esp_id]["history"].append(data)
    eval_ = predictor.evaluate(esp_data[esp_id]["history"])
    save_record(esp_id, data, eval_)
    if data["alerts"]:
        alert_sensor(esp_id, data["alerts"], data)
    if eval_["risk"] >= settings.risk_threshold:
        report_failure(esp_id, eval_, data)


def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(settings.mqtt_broker, settings.mqtt_port, settings.mqtt_keepalive)
    client.loop_forever()


threading.Thread(target=start_mqtt, daemon=True).start()
