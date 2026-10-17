
"""JSON persistence for ticket collections."""

import json
from pathlib import Path

from campusflow.tickets import (
    calculate_priority,
    validate_ticket_details,
)

DEFAULT_STORAGE_PATH = Path("data/tickets.json")

ALLOWED_STATUSES = {"open", "in_progress", "resolved"}


def validate_stored_notes(ticket_id, notes):
    """Validate notes attached to a ticket."""
    if not isinstance(notes, list):
        raise ValueError(f"Ticket {ticket_id} notes must be a list.")

    seen_ids = set()

    for note in notes:
        if not isinstance(note, dict):
            raise ValueError(f"Ticket {ticket_id} contains an invalid note.")

        note_id = note.get("note_id")
        author = note.get("author")
        message = note.get("message")

        if (
            not isinstance(note_id, str)
            or not note_id.startswith("N")
            or not note_id[1:].isdigit()
            or int(note_id[1:]) < 1
        ):
            raise ValueError(f"Ticket {ticket_id} has an invalid note ID.")

        if note_id in seen_ids:
            raise ValueError(
                f"Ticket {ticket_id} has duplicate note IDs."
            )
        seen_ids.add(note_id)

        if not isinstance(author, str) or not author.strip():
            raise ValueError(
                f"Ticket {ticket_id} has an invalid note author."
            )

        if (
            not isinstance(message, str)
            or not 5 <= len(message.strip()) <= 300
        ):
            raise ValueError(
                f"Ticket {ticket_id} has an invalid note message."
            )


def save_tickets(tickets, filepath=DEFAULT_STORAGE_PATH):
    """Write tickets as JSON, using a temporary file to avoid partial writes."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")

    try:
        temporary_path.write_text(
            json.dumps(tickets, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    return path


def validate_stored_tickets(data):
    """Validate the structure and contents of saved tickets."""
    if not isinstance(data, list):
        raise ValueError("Ticket file must contain a JSON list.")

    seen_ids = set()
    seen_note_ids = set()

    for index, ticket in enumerate(data):
        if not isinstance(ticket, dict):
            raise ValueError(
                f"Ticket at position {index} must be a dictionary."
            )

        ticket_id = ticket.get("id")

        if (
            not isinstance(ticket_id, str)
            or len(ticket_id) < 2
            or ticket_id[0] != "T"
            or not ticket_id[1:].isdigit()
            or int(ticket_id[1:]) < 1
        ):
            raise ValueError(
                f"Ticket at position {index} has an invalid ticket ID."
            )

        if ticket_id in seen_ids:
            raise ValueError(f"Duplicate ticket ID: {ticket_id}")

        seen_ids.add(ticket_id)

        required_fields = {
            "id",
            "title",
            "category",
            "urgency",
            "affected_users",
            "priority",
            "status",
            "assigned_to",
        }

        missing_fields = required_fields - ticket.keys()

        if missing_fields:
            raise ValueError(
                f"Ticket {ticket_id} is missing fields: "
                f"{', '.join(sorted(missing_fields))}"
            )

        try:
            title, category, urgency, affected_users = (
                validate_ticket_details(
                    ticket["title"],
                    ticket["category"],
                    ticket["urgency"],
                    ticket["affected_users"],
                )
            )
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Ticket {ticket_id} contains invalid details: {exc}"
            ) from exc

        expected_priority = calculate_priority(urgency, affected_users)

        if ticket["priority"] != expected_priority:
            raise ValueError(
                f"Ticket {ticket_id} has an incorrect priority. "
                f"Expected {expected_priority}."
            )

        if ticket["status"] not in ALLOWED_STATUSES:
            raise ValueError(
                f"Ticket {ticket_id} has an invalid status."
            )

        assigned_to = ticket["assigned_to"]

        # Older saved tickets without notes are treated as having no notes.
        notes = ticket.get("notes", [])
        validate_stored_notes(ticket_id, notes)

        # Reject note IDs duplicated on this ticket or any earlier ticket.
        for note in notes:
            note_id = note["note_id"]

            if note_id in seen_note_ids:
                raise ValueError(
                    f"Duplicate note ID across tickets: {note_id}"
                )

            seen_note_ids.add(note_id)

        ticket.setdefault("notes", notes)

        if assigned_to is not None and (
            not isinstance(assigned_to, str) or not assigned_to.strip()
        ):
            raise ValueError(
                f"Ticket {ticket_id} has an invalid assignee."
            )

    return data


def load_tickets(filepath=DEFAULT_STORAGE_PATH):
    """Load and validate tickets from JSON."""
    path = Path(filepath)

    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Ticket file contains invalid JSON: {path}"
        ) from exc
    except OSError as exc:
        raise ValueError(
            f"Could not read ticket file: {path}"
        ) from exc

    return validate_stored_tickets(data)
