
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

def send_email_notification(recipient, subject, body):
    """Send one email notification using the configured Gmail account."""
    sender_email, sender_password, _ = load_email_settings()

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as smtp:
        smtp.starttls()
        smtp.login(sender_email, sender_password)
        smtp.send_message(message)

def send_new_ticket_notification(ticket):
    """Notify central support when a ticket is created."""
    _, _, support_email = load_email_settings()

    send_email_notification(
        support_email,
        f"New CampusFlowNext Ticket - {ticket['id']} - "
        f"{ticket['priority'].upper()}",
        (
            "CAMPUSFLOWNEXT TICKET CREATION\n"
            "Notification: New Ticket Created\n"
            "Sent by: CampusFlow Help Desk\n\n"
            "A new CampusFlowNext ticket has been created "
            "and requires the support team's attention.\n\n"
            f"Ticket ID: {ticket['id']}\n"
            f"Title: {ticket['title']}\n"
            f"Category: {ticket['category']}\n"
            f"Priority: {ticket['priority'].upper()}\n"
            f"Status: {ticket['status'].replace('_', ' ').title()}\n"
        ),
    )

def get_staff_email(staff_name):
    """Return a staff member's configured email address, if available."""
    if not staff_name:
        return None

    key = "_".join(
        part
        for part in staff_name.upper()
        .replace(".", "")
        .replace("(", " ")
        .replace(")", " ")
        .split()
    )
    staff_email_key = f"CAMPUSFLOW_STAFF_EMAIL_{key}"

    env_path = Path(__file__).resolve().parent.parent / ".env"

    if not env_path.is_file():
        return None

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        name, value = line.split("=", 1)

        if name.strip() == staff_email_key:
            email = value.strip().strip('"').strip("'")
            return email or None

    return None


def send_assignment_notification(ticket):
    """Notify the assigned staff member when an address is configured."""
    assignee = ticket.get("assigned_to")

    if not assignee:
        return

    # Convert the staff name into a clean .env variable name.
    # Example: "Mr. Samuel" -> "MR_SAMUEL"
    key = "_".join(
        part
        for part in assignee.upper()
        .replace(".", "")
        .replace("(", " ")
        .replace(")", " ")
        .split()
    )

    staff_email_key = f"CAMPUSFLOW_STAFF_EMAIL_{key}"

    env_path = Path(__file__).resolve().parent.parent / ".env"
    settings = {}

    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                name, value = line.split("=", 1)
                settings[name.strip()] = (
                    value.strip().strip('"').strip("'")
                )

        recipient = get_staff_email(assignee)

    if not recipient:
        key = "_".join(
            part
            for part in assignee.upper()
            .replace(".", "")
            .replace("(", " ")
            .replace(")", " ")
            .split()
        )

        raise ValueError(
            f"No email configured for {assignee}. "
            f"Add CAMPUSFLOW_STAFF_EMAIL_{key} to .env."
        )

    send_email_notification(
        recipient,
        f"Ticket Assigned - {ticket['id']}",
        (
            "CAMPUSFLOWNEXT TICKET ASSIGNMENT\n"
            "Assigned by: CampusFlow Support Team\n"
            "Sent by: CampusFlow Help Desk\n\n"
            "A CampusFlowNext ticket has been assigned to you.\n\n"
            f"Ticket ID: {ticket['id']}\n"
            f"Title: {ticket['title']}\n"
            f"Category: {ticket['category']}\n"
            f"Priority: {ticket['priority'].upper()}\n"
            f"Status: {ticket['status'].replace('_', ' ').title()}\n"
        ),
    )

def send_status_notification(ticket, previous_status):
    """Notify central support about important status changes."""
    _, _, support_email = load_email_settings()
    status = ticket["status"]

    if status == previous_status:
        return

    if status not in {"in_progress", "resolved", "closed"}:
        return

    if status == "in_progress":
        subject = f"Ticket In Progress - {ticket['id']}"
    else:
        subject = f"Ticket {status.title()} - {ticket['id']}"

    send_email_notification(
        support_email,
        subject,
        (
            "CAMPUSFLOWNEXT TICKET STATUS UPDATE\n"
            f"Reported by: {ticket.get('assigned_to') or 'Unassigned'}\n"
            "Destination: CampusFlow Support Team\n\n"
            "The assigned staff member has updated the ticket status.\n\n"
            f"Ticket ID: {ticket['id']}\n"
            f"Title: {ticket['title']}\n"
            f"Category: {ticket['category']}\n"
            f"Priority: {ticket['priority'].upper()}\n"
            f"Current Status: "
            f"{ticket['status'].replace('_', ' ').title()}\n"
        ),
    )

def send_feedback_note_notification(ticket, note):
    """Notify support of feedback and identify the staff author."""
    _, _, support_email = load_email_settings()

    author = str(note.get("author", "Unknown")).strip() or "Unknown"
    author_email = get_staff_email(author)

    if author_email:
        staff_email_line = f"Staff email: {author_email}\n"
    else:
        staff_email_line = (
            "Staff email: No matching email configured in .env\n"
        )

    send_email_notification(
        support_email,
        f"Staff Feedback - {ticket['id']} - {note['note_id']}",
        (
            "CAMPUSFLOWNEXT STAFF FEEDBACK\n"
            "Sent by: CampusFlow Help Desk\n"
            "Destination: CampusFlow Support Team\n\n"
            "A feedback note has been recorded for a ticket.\n\n"
            f"Ticket ID: {ticket['id']}\n"
            f"Ticket title: {ticket['title']}\n"
            f"Note ID: {note['note_id']}\n"
            f"Staff member: {author}\n"
            f"{staff_email_line}"
            f"Timestamp: {note.get('timestamp', 'Not recorded')}\n\n"
            f"Feedback:\n{note['message']}\n"
        ),
    )