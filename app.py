from flask import Flask, jsonify, render_template, request, send_file
import threading, csv
from config import Settings
from mqtt_handler import esp_data, start_mqtt
import history

settings = Settings()
app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/graphiques")
def graphiques():
    return render_template("graphiques.html")


@app.route("/historique")
def historique():
    # The template will initialize DataTables; no need to pass records here
    return render_template("historique.html")


@app.route("/api/graph_data")
def api_graph_data():
    period = request.args.get("period", "1h")  # optional filtering by period

    # Map JS metric keys to CSV headers
    METRICS = {
        "temperature": "Température (°C)",
        "humidity": "Humidité (%)",
        "vibration": "Vibration (mm/s)",
        "voltage": "Tension (V)",
        "current": "Courant (A)",
        "risk": "Risque de Panne (%)",
    }

    # Initialize output structure
    data = {esp: {m: [] for m in METRICS} for esp in ["esp32_1", "esp32_2"]}

    # Read CSV and group by esp32_id
    with open(settings.data_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            esp = row.get("esp32_id", "esp32_1")
            if esp not in data:
                continue
            ts = row.get("Date et Heure")
            if not ts:
                continue
            for key, header in METRICS.items():
                raw = row.get(header)
                if not raw:
                    continue
                try:
                    y = float(raw)
                except ValueError:
                    continue
                data[esp][key].append({"x": ts, "y": y})

    return jsonify(data)


@app.route("/api/history/<esp32_id>")
def api_history(esp32_id):
    # Read CSV with French headers and ignore esp32_id (single source)
    data = []
    with open(settings.data_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(
                {
                    "timestamp": row.get("Date et Heure"),
                    "temperature": row.get("Température (°C)"),
                    "humidity": row.get("Humidité (%)"),
                    "status": row.get("Statut"),
                    "alerts": row.get("Alertes"),
                    "risk": row.get("Risque de Panne (%)"),
                    "motor_status": row.get("Statut Moteur"),
                    "details": row.get("Détails"),
                }
            )
    return jsonify({"data": data})


@app.route("/download_csv")
def download_csv():
    return send_file(
        settings.data_file,
        mimetype='text/csv',
        as_attachment=True,
        download_name='historique.csv'
    )

if __name__ == "__main__":
    threading.Thread(target=start_mqtt, daemon=True).start()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,  # ← turns on debugger + reloader
        use_reloader=True,  # ← explicitly enable the reloader
        threaded=True,
    )
