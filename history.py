import csv
from datetime import datetime
from config import Settings

settings = Settings()


def init_history():
    if not settings.data_file.exists():
        with open(settings.data_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "timestamp",
                    "esp32_id",
                    "temperature",
                    "humidity",
                    "vibration",
                    "voltage",
                    "current",
                    "status",
                    "alerts",
                    "risk",
                    "motor_status",
                ]
            )


def save_record(esp_id: str, data: dict, eval_: dict) -> None:
    with open(settings.data_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                datetime.now().isoformat(),
                esp_id,
                data["temperature"],
                data["humidity"],
                data["vibration"],
                data["voltage"],
                data["current"],
                data["status"],
                "|".join(data["alerts"]),
                f"{eval_['risk']:.3f}",
                eval_["motor_status"],
            ]
        )
