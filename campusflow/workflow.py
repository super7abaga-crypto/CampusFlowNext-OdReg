"""Operations for finding, assigning, and updating tickets."""

from datetime import datetime

from campusflow.staff import STAFF_MEMBERS


ALLOWED_STATUSES = {"open", "in_progress", "resolved", "closed"}


def normalize_status(status):
    """Normalize a ticket status for consistent comparisons."""
    if not isinstance(status, str):
        return ""
    return status.strip().lower()


def normalize_name(name):
    """Normalize a staff name for comparison."""
    if not isinstance(name, str):
        return ""
    return name.strip().casefold().replace("(hoc)", "").strip()


def ticket_number(ticket):
    """Return the numeric part of a ticket ID for sorting."""
    ticket_id = str(ticket.get("id", ""))

    if (
        len(ticket_id) > 1
        and ticket_id[0].upper() == "T"
        and ticket_id[1:].isdigit()
    ):
        return int(ticket_id[1:])

    # Malformed IDs sort after correctly formatted IDs.
    return float("inf")


def find_ticket(tickets, ticket_id):
    """Return a ticket by ID, ignoring ID letter case."""
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("Please provide a ticket ID.")

    wanted = ticket_id.strip().upper()

    for ticket in tickets:
        if (
            isinstance(ticket, dict)
            and str(ticket.get("id", "")).strip().upper() == wanted
        ):
            return ticket

    raise ValueError(f"Ticket {wanted} was not found.")


def assign_ticket(tickets, ticket_id, assignee):
    """Assign or reassign a ticket unless it is resolved or closed."""
    ticket = find_ticket(tickets, ticket_id)
    status = normalize_status(ticket.get("status"))

    if status in {"resolved", "closed"}:
        raise ValueError(
            f"Ticket {ticket_id} cannot be reassigned "
            f"because its status is {status}. "
            "Reopen the ticket before changing its assignment."
        )

    if not isinstance(assignee, str) or not assignee.strip():
        raise ValueError("Staff name cannot be empty.")

    entered_name = normalize_name(assignee)

    staff_member = next(
        (
            staff
            for staff in STAFF_MEMBERS
            if normalize_name(staff.get("name", "")) == entered_name
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
            f"{staff_member['name']} is currently unavailable "
            "for assignment."
        )

    previous_assignee = ticket.get("assigned_to")
    official_name = staff_member["name"]

    if (
        isinstance(previous_assignee, str)
        and previous_assignee.strip()
        and normalize_name(previous_assignee)
        == normalize_name(official_name)
    ):
        raise ValueError(
            f"Ticket {ticket['id']} is already assigned to "
            f"{official_name}. Choose a different staff member "
            "if you want to reassign it."
        )

    # Save the assignment only after validation succeeds.
    ticket["assigned_to"] = official_name

    if isinstance(previous_assignee, str) and previous_assignee.strip():
        record_ticket_history(
            ticket,
            "reassigned",
            f"Reassigned from {previous_assignee} to {official_name}",
        )
    else:
        record_ticket_history(
            ticket,
            "assigned",
            f"Assigned to {official_name}",
        )

    return ticket


def update_ticket_status(tickets, ticket_id, status):
    """Update a ticket's status only when the transition is valid."""
    if not isinstance(status, str):
        raise ValueError(
            "Invalid status. Choose open, in_progress, resolved, or closed."
        )

    status = normalize_status(status)

    if status not in ALLOWED_STATUSES:
        raise ValueError(
            "Invalid status. Choose open, in_progress, resolved, or closed."
        )

    ticket = find_ticket(tickets, ticket_id)
    previous_status = normalize_status(ticket.get("status"))

    if previous_status not in ALLOWED_STATUSES:
        raise ValueError(
            f"Ticket {ticket['id']} has an invalid current status. "
            "Correct its status before updating it."
        )

    if previous_status == status:
        return ticket

    if previous_status == "closed" and status != "open":
        raise ValueError(
            "A closed ticket must be reopened to open "
            "before it can move to another status."
        )

    if previous_status == "resolved" and status not in {"closed", "open"}:
        raise ValueError(
            "A resolved ticket can only be closed or reopened to open."
        )

    if previous_status == "open" and status != "in_progress":
        raise ValueError(
            "An open ticket must move to in_progress "
            "before it can be resolved or closed."
        )

    if previous_status == "in_progress" and status == "closed":
        raise ValueError(
            "An in-progress ticket must be resolved "
            "before it can be closed."
        )

    if (
        status in {"in_progress", "resolved", "closed"}
        and not str(ticket.get("assigned_to") or "").strip()
    ):
        raise ValueError(
            f"Ticket {ticket_id} cannot move to {status} "
            "because it has not been assigned to a staff member. "
            "Please assign the ticket first."
        )

    ticket["status"] = status

    record_ticket_history(
        ticket,
        "status_changed",
        f"Status changed from {previous_status} to {status}",
    )

    return ticket


def get_priority_queue(tickets):
    """Return open tickets sorted by priority, affected users, and ID."""
    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    open_tickets = [
        ticket
        for ticket in tickets
        if normalize_status(ticket.get("status")) == "open"
    ]

    def affected_users_count(ticket):
        try:
            return max(0, int(ticket.get("affected_users", 0)))
        except (TypeError, ValueError):
            return 0

    return sorted(
        open_tickets,
        key=lambda ticket: (
            priority_order.get(
                str(ticket.get("priority", "")).strip().lower(),
                4,
            ),
            -affected_users_count(ticket),
            ticket_number(ticket),
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
            if normalize_status(ticket.get("status")) != normalize_status(status):
                continue

        if priority is not None:
            ticket_priority = str(ticket.get("priority", "")).strip().lower()
            requested_priority = str(priority).strip().lower()

            if ticket_priority != requested_priority:
                continue

        if category is not None:
            ticket_category = str(ticket.get("category", "")).strip().lower()
            requested_category = str(category).strip().lower()

            if ticket_category != requested_category:
                continue

        if assigned_to is not None:
            current_assignee = ticket.get("assigned_to")

            if not isinstance(current_assignee, str):
                continue

            if (
                current_assignee.strip().casefold()
                != assigned_to.strip().casefold()
            ):
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
    """Filter tickets and return them sorted by priority and ticket ID."""
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
            priority_order.get(
                str(ticket.get("priority", "")).strip().lower(), 4
            ),
            ticket_number(ticket),
        ),
    )


def search_tickets(
    tickets,
    keyword=None,
    status=None,
    priority=None,
    category=None,
    assigned_to=None,
):
    """Search tickets by title and apply optional filters."""
    filtered_tickets = filter_and_sort_tickets(
        tickets,
        status=status,
        priority=priority,
        category=category,
        assigned_to=assigned_to,
    )

    if keyword is None or not keyword.strip():
        return filtered_tickets

    normalized_keyword = keyword.strip().casefold()
    search_results = []

    for ticket in filtered_tickets:
        ticket_title = str(ticket.get("title", "")).casefold()

        if normalized_keyword in ticket_title:
            search_results.append(ticket)

    return search_results


def record_ticket_history(ticket, action, details):
    """Record an event in a ticket's history."""
    event = {
        "timestamp": datetime.now()
        .astimezone()
        .isoformat(timespec="seconds"),
        "action": action,
        "details": details,
    }

    ticket.setdefault("history", []).append(event)

    return event
