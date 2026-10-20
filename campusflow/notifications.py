"""Email notifications for CampusFlowNext ticket events."""

import smtplib
from email.message import EmailMessage
from pathlib import Path


def load_email_settings():
    """Load email settings from the project's .env file."""

    env_path = Path(__file__).resolve().parent.parent / ".env"

    if not env_path.is_file():
        raise ValueError("The project .env file was not found.")

    settings = {}

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        settings[key.strip()] = value.strip().strip('"').strip("'")

    sender_email = settings.get("CAMPUSFLOW_EMAIL")
    sender_password = settings.get("CAMPUSFLOW_EMAIL_PASSWORD")
    support_email = settings.get("CAMPUSFLOW_SUPPORT_EMAIL")

    if not sender_email or not sender_password or not support_email:
        raise ValueError(
            "Check that CAMPUSFLOW_EMAIL, "
            "CAMPUSFLOW_EMAIL_PASSWORD, and "
            "CAMPUSFLOW_SUPPORT_EMAIL are set in .env."
        )

    return sender_email, sender_password, support_email


def send_new_ticket_notification(ticket):
    """Send a new-ticket notification to the central support inbox."""

    sender_email, sender_password, support_email = (
        load_email_settings()
    )

    message = EmailMessage()

    message["From"] = sender_email
    message["To"] = support_email
    message["Subject"] = (
        f"New CampusFlowNext Ticket — "
        f"{ticket['id']} — {ticket['priority'].upper()}"
    )

    message.set_content(
        f"""
A new IT support complaint has been registered
in CampusFlowNext.

Ticket ID: {ticket['id']}
Title: {ticket['title']}
Category: {ticket['category']}
Urgency: {ticket['urgency'].title()}
Affected users: {ticket['affected_users']}
Priority: {ticket['priority'].upper()}
Status: {ticket['status'].replace('_', ' ').title()}

Please review this ticket and take the necessary action.

CampusFlowNext Ticket Management System
""".strip()
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender_email, sender_password)
        smtp.send_message(message)