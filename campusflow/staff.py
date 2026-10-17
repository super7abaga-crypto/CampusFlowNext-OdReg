"""Staff records and staff recommendation helpers."""

STAFF_MEMBERS = [
    # Network support
    {
        "name": "Mr. Odeh",
        "speciality": "Network",
        "available": True,
    },
    {
        "name": "Mr. Kingsley (HOC)",
        "speciality": "Network",
        "available": True,
    },
    {
        "name": "Ms. Chijioke",
        "speciality": "Network",
        "available": True,
    },

    # Hardware support
    {
        "name": "Big 7",
        "speciality": "Hardware",
        "available": True,
    },
    {
        "name": "Mr. Myles",
        "speciality": "Hardware",
        "available": True,
    },
    {
        "name": "Mr. Ayuba",
        "speciality": "Hardware",
        "available": True,
    },

    # Software support
    {
        "name": "Mr. Kingsley (Software)",
        "speciality": "Software",
        "available": True,
    },
    {
        "name": "Mr. Onche",
        "speciality": "Software",
        "available": True,
    },
    {
        "name": "Ms. Queen",
        "speciality": "Software",
        "available": True,
    },

    # Other support
    {
        "name": "Mr. Wealth",
        "speciality": "Other",
        "available": True,
    },
    {
        "name": "Mr. Samuel",
        "speciality": "Other",
        "available": True,
    },
    {
        "name": "Mr. Edward",
        "speciality": "Other",
        "available": True,
    },
]

BUSY_THRESHOLD = 3
INACTIVE_STATUSES = {"resolved", "closed"}


def normalize_name(name):
    """Normalize a staff name for comparison."""
    if not isinstance(name, str):
        return ""

    return " ".join(
        name.strip().casefold().replace("(hoc)", "").split()
    )


def normalize_status(status):
    """Normalize a ticket status for comparison."""
    if not isinstance(status, str):
        return ""

    return status.strip().lower()


def get_active_workloads(tickets):
    """Count active tickets assigned to each staff member."""
    workloads = {}

    for ticket in tickets:
        assignee = normalize_name(ticket.get("assigned_to"))

        if not assignee:
            continue

        status = normalize_status(ticket.get("status"))

        if status in INACTIVE_STATUSES:
            continue

        workloads[assignee] = workloads.get(assignee, 0) + 1

    return workloads


def recommend_staff(ticket, tickets, staff_members=None):
    """Recommend an available specialist with the lowest workload."""
    if staff_members is None:
        staff_members = STAFF_MEMBERS

    if not isinstance(ticket, dict):
        raise ValueError("Please provide a valid ticket.")

    category = ticket.get("category", "")

    if not isinstance(category, str) or not category.strip():
        raise ValueError("Please provide a ticket category.")

    category = category.strip().casefold()
    workloads = get_active_workloads(tickets)

    candidates = [
        staff
        for staff in staff_members
        if isinstance(staff.get("speciality"), str)
        and staff["speciality"].strip().casefold() == category
        and staff.get("available") is True
        and isinstance(staff.get("name"), str)
        and staff["name"].strip()
        and workloads.get(normalize_name(staff["name"]), 0)
        < BUSY_THRESHOLD
    ]

    if not candidates:
        return None

    # If workloads are tied, retain the original staff-list order.
    return min(
        candidates,
        key=lambda staff: workloads.get(
            normalize_name(staff["name"]), 0
        ),
    )


def summarize_staff_workload(tickets, staff_members=None):
    """Summarize staff workload and calculate availability status."""
    if staff_members is None:
        staff_members = STAFF_MEMBERS

    workloads = get_active_workloads(tickets)
    staff_summary = []

    for staff in staff_members:
        staff_name = staff["name"]
        normalized_staff_name = normalize_name(staff_name)

        assigned_tickets = [
            ticket
            for ticket in tickets
            if normalize_name(ticket.get("assigned_to"))
            == normalized_staff_name
        ]

        active_tickets = [
            ticket
            for ticket in assigned_tickets
            if normalize_status(ticket.get("status"))
            not in INACTIVE_STATUSES
        ]

        resolved_closed_tickets = [
            ticket
            for ticket in assigned_tickets
            if normalize_status(ticket.get("status"))
            in INACTIVE_STATUSES
        ]

        manually_available = staff.get("available", False)

        if manually_available is not True:
            availability_status = "Unavailable"
        elif workloads.get(normalized_staff_name, 0) >= BUSY_THRESHOLD:
            availability_status = "Busy"
        else:
            availability_status = "Available"

        staff_summary.append({
            "name": staff_name,
            "speciality": staff["speciality"],
            "available": manually_available,
            "status": availability_status,
            "active": len(active_tickets),
            "active_ticket_ids": [
                ticket.get("id", "Unknown")
                for ticket in active_tickets
            ],
            "open": sum(
                normalize_status(ticket.get("status")) == "open"
                for ticket in assigned_tickets
            ),
            "in_progress": sum(
                normalize_status(ticket.get("status")) == "in_progress"
                for ticket in assigned_tickets
            ),
            "resolved_closed": len(resolved_closed_tickets),
            "resolved_closed_ticket_ids": [
                ticket.get("id", "Unknown")
                for ticket in resolved_closed_tickets
            ],
        })

    unassigned = sum(
        1
        for ticket in tickets
        if not normalize_name(ticket.get("assigned_to"))
        and normalize_status(ticket.get("status"))
        not in INACTIVE_STATUSES
    )

    return {
        "staff": staff_summary,
        "unassigned": unassigned,
    }

def recommend_staff_options(ticket, tickets, staff_members=None):
    """Return all eligible available specialists, ranked by workload."""

    if staff_members is None:
        staff_members = STAFF_MEMBERS

    if not isinstance(ticket, dict):
        raise ValueError("Invalid ticket.")

    category = ticket.get("category", "")

    if not isinstance(category, str) or not category.strip():
        raise ValueError("Please provide a ticket category.")

    category = category.strip().casefold()
    workloads = get_active_workloads(tickets)
    candidates = []

    for staff in staff_members:
        name = staff.get("name", "")
        speciality = staff.get("speciality", "")

        if not isinstance(name, str) or not name.strip():
            continue

        if not isinstance(speciality, str):
            continue

        if speciality.strip().casefold() != category:
            continue

        if staff.get("available") is not True:
            continue

        active_workload = workloads.get(normalize_name(name), 0)

        if active_workload >= BUSY_THRESHOLD:
            continue

        candidates.append({
            "name": name,
            "speciality": speciality,
            "active": active_workload,
            "status": "Available",
        })

    return sorted(candidates, key=lambda staff: staff["active"])