"""Validation and creation of ticket notes."""

from datetime import datetime

def generate_note_id(tickets):
    """Return the next note ID across the ticket collection."""
    highest_id = 0

    for ticket in tickets:
        for note in ticket.get("notes", []):
            note_id = note.get("note_id", "")

            if (
                isinstance(note_id, str)
                and note_id.startswith("N")
                and note_id[1:].isdigit()
            ):
                number = int(note_id[1:])
                highest_id = max(highest_id, number)

    return f"N{highest_id + 1:03d}"


def make_note_adder(tickets):
    """Create an add_note function connected to the ticket collection."""

    def add_note(ticket_id, author, message):
        """Add a validated note to an open or in-progress ticket."""
        if not isinstance(ticket_id, str) or not ticket_id.strip():
            raise ValueError("Ticket ID cannot be empty.")

        if not isinstance(author, str) or not author.strip():
            raise ValueError("Note author cannot be empty.")

        if not isinstance(message, str):
            raise ValueError("Note message must be text.")

        normalized_id = ticket_id.strip().upper()
        author = author.strip()
        message = message.strip()

        if not 5 <= len(message) <= 300:
            raise ValueError(
                "Note message must be between 5 and 300 characters."
            )

        ticket = next(
            (
                item for item in tickets
                if item.get("id") == normalized_id
            ),
            None,
        )

        if ticket is None:
            raise ValueError(f"Ticket {normalized_id} was not found.")

        status = ticket.get("status")

        if status == "resolved":
            raise ValueError(
                "This ticket is resolved. Reopen the ticket "
                "before adding a note."
            )

        if status == "closed":
            raise ValueError(
                "This ticket is closed and cannot receive notes."
            )

        if status not in {"open", "in_progress"}:
            raise ValueError(
                "Notes can only be added to open or in-progress tickets."
            )

        notes = ticket.get("notes")

        if not isinstance(notes, list):
            raise ValueError("Ticket notes must be a list.")

        for note in notes:
            if not isinstance(note, dict):
                raise ValueError("Ticket contains an invalid note.")

            existing_id = note.get("note_id")

            if (
                not isinstance(existing_id, str)
                or not existing_id.startswith("N")
                or not existing_id[1:].isdigit()
                or int(existing_id[1:]) < 1
            ):
                raise ValueError("Ticket contains an invalid note ID.")

        new_note = {
    "note_id": generate_note_id(tickets),
    "author": author,
    "message": message,
    "timestamp": datetime.now().astimezone().isoformat(
        timespec="seconds"
    ),
}

        notes.append(new_note)
        return new_note

    return add_note