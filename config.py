from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    mqtt_broker: str = Field("localhost", env="MQTT_BROKER")
    mqtt_port: int = Field(1883, env="MQTT_PORT")
    mqtt_keepalive: int = Field(60, env="MQTT_KEEPALIVE")
    topics: dict = Field(
        default_factory=lambda: {
            "esp32_1": "sensor/dht22/esp32_1",
            "esp32_2": "sensor/dht22/esp32_2",
        }
    )

    model_path: Path = Field(Path("models/motor_failure_rnn.h5"), env="MODEL_PATH")
    sequence_length: int = Field(10, env="SEQUENCE_LENGTH")
    input_features: int = Field(5, env="INPUT_FEATURES")
    risk_threshold: float = Field(0.7, env="RISK_THRESHOLD")

    smtp_server: str = Field("smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(465, env="SMTP_PORT")
    email_user: str = Field(..., env="EMAIL_USER")
    email_password: str = Field(..., env="EMAIL_PASSWORD")
    email_receiver: str = Field(..., env="EMAIL_RECEIVER")

    data_file: Path = Field(Path("historique_complet.csv"), env="DATA_FILE")

    class Config:
        env_file = ".env"
