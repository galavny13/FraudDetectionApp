# backend/app/send_email.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "example@domain.com")

def send_fraud_alert(to_email: str, explanation: str):
    """
    Sends an email alert if fraud is detected.
    """
    if not SENDGRID_API_KEY or not to_email:
        print("[send_email] Missing SendGrid API key or to_email, skipping.")
        return

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject="[FRAUD ALERT] Suspicious Transaction Detected",
        html_content=f"""
        <h1>Fraud Alert</h1>
        <p>{explanation}</p>
        """
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print("[send_email] Status:", response.status_code)
    except Exception as e:
        print("[send_email] Error sending email:", e)
