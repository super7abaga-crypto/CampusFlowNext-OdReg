"""Operations for finding, assigning, and updating tickets."""

from datetime import datetime
from campusflow.staff import STAFF_MEMBERS
ALLOWED_STATUSES = {"open", "in_progress", "resolved", "closed"}


def find_ticket(tickets, ticket_id):
    """Return a ticket by ID, ignoring ID letter case."""
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("Please provide a ticket ID.")
    wanted = ticket_id.strip().upper()
    for ticket in tickets:
        if isinstance(ticket, dict) and str(ticket.get("id", "")).upper() == wanted:
            return ticket
    raise ValueError(f"Ticket {wanted} was not found.")


def assign_ticket(tickets, ticket_id, assignee):
    """Assign a ticket to an available staff member using flexible name matching."""

    ticket = find_ticket(tickets, ticket_id)

    if not assignee or not assignee.strip():
        raise ValueError("Staff name cannot be empty.")

    def normalize_name(name):
        """Normalize a staff name for comparison."""
        return (
            name.strip()
            .casefold()
            .replace("(hoc)", "")
            .strip()
        )

    entered_name = normalize_name(assignee)

    staff_member = next(
        (
            staff
            for staff in STAFF_MEMBERS
            if normalize_name(staff["name"]) == entered_name
        ),
        None,
    )

    if staff_member is None:
        valid_names = ", ".join(
            staff["name"] for staff in STAFF_MEMBERS
        )

        raise ValueError(
            f"Staff member '{assignee.strip()}' was not found. "
            f"Choose from: {valid_names}"
        )

    if not staff_member.get("available", False):
        raise ValueError(
            f"{staff_member['name']} is currently unavailable for assignment."
        )

    previous_assignee = ticket.get("assigned_to")

    # Always store the official name from STAFF_MEMBERS.
    ticket["assigned_to"] = staff_member["name"]

    if previous_assignee != staff_member["name"]:
        if previous_assignee:
            record_ticket_history(
                ticket,
                "reassigned",
                f"Reassigned from {previous_assignee} to "
                f"{staff_member['name']}",
            )
        else:
            record_ticket_history(
                ticket,
                "assigned",
                f"Assigned to {staff_member['name']}",
            )

    return ticket

def update_ticket_status(tickets, ticket_id, status):
    """Update a ticket's status and record the change."""

    if not isinstance(status, str):
        raise ValueError(
            "Invalid status. Choose open, in_progress, resolved, or closed."
        )

    status = status.strip().lower()

    if status not in ALLOWED_STATUSES:
        raise ValueError(
            "Invalid status. Choose open, in_progress, resolved, or closed."
        )

    ticket = find_ticket(tickets, ticket_id)
    previous_status = ticket.get("status")

    ticket["status"] = status

    if previous_status != status:
        record_ticket_history(
            ticket,
            "status_changed",
            f"Status changed from {previous_status} to {status}",
        )

    return ticket

def get_priority_queue(tickets):
    """Return unresolved tickets sorted by priority and numeric ID."""

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    unresolved_tickets = [
        ticket
        for ticket in tickets
        if ticket.get("status") not in {"resolved", "closed"}
    ]

    return sorted(
        unresolved_tickets,
        key=lambda ticket: (
            priority_order.get(ticket.get("priority"), 4),
            int(ticket["id"][1:]),
        ),
    )

def filter_tickets(
    tickets,
    status=None,
    priority=None,
    category=None,
    assigned_to=None,
):
    """Return tickets matching the supplied filters."""

    filtered = []

    for ticket in tickets:
        if status is not None:
            if ticket.get("status", "").lower() != status.strip().lower():
                continue

        if priority is not None:
            if ticket.get("priority", "").lower() != priority.strip().lower():
                continue

        if category is not None:
            if ticket.get("category", "").lower() != category.strip().lower():
                continue

        if assigned_to is not None:
            current_assignee = ticket.get("assigned_to")

            if not isinstance(current_assignee, str):
                continue

            if current_assignee.strip().lower() != assigned_to.strip().lower():
                continue

        filtered.append(ticket)

    return filtered

def filter_and_sort_tickets(
    tickets,
    status=None,
    priority=None,
    category=None,
    assigned_to=None,
):
    """Filter tickets and return them sorted by priority."""

    filtered = filter_tickets(
        tickets,
        status=status,
        priority=priority,
        category=category,
        assigned_to=assigned_to,
    )

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    return sorted(
        filtered,
        key=lambda ticket: (
            priority_order.get(ticket.get("priority"), 4),
            int(ticket["id"][1:]),
        ),
    )

def record_ticket_history(ticket, action, details):
    """Record an event in a ticket's history."""

    event = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "action": action,
        "details": details,
    }

    ticket.setdefault("history", []).append(event)

    return event