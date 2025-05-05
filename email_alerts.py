import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Settings

settings = Settings()


def send_email(subject: str, body_html: str) -> bool:
    msg = MIMEMultipart()
    msg["From"] = settings.email_user
    msg["To"] = settings.email_receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body_html, "html"))
    try:
        with smtplib.SMTP_SSL(settings.smtp_server, settings.smtp_port) as smtp:
            smtp.login(settings.email_user, settings.email_password)
            smtp.send_message(msg)
        return True
    except Exception:
        return False


def alert_sensor(esp_id: str, alerts: list, data: dict) -> None:
    subj = f"[ALERTE] {esp_id} - {len(alerts)} anomalies détectées"
    details = "".join(f"<li>{a}</li>" for a in alerts)
    body = f"<h3>Alertes pour {esp_id}</h3><ul>{details}</ul>"
    send_email(subj, body)


def report_failure(esp_id: str, evaluation: dict, data: dict) -> None:
    subj = f"[PANNE] {esp_id} - Statut: {evaluation['motor_status']}"
    body = f"<p>Risque: {evaluation['risk'] * 100:.1f}%</p><p>Statut: {evaluation['motor_status']}</p>"
    send_email(subj, body)
