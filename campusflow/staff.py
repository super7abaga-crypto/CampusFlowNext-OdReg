"""Staff records and staff recommendation helpers."""

STAFF_MEMBERS = [
    {
        "name": "Mr. Odeh",
        "speciality": "Network",
        "available": True,
    },
    {
        "name": "Ms. Regina",
        "speciality": "Hardware",
        "available": True,
    },
    {
        "name": "Mr. Kingsley (HOC)",
        "speciality": "Software",
        "available": True,
    },
    {
        "name": "Ms. Juliet",
        "speciality": "Other",
        "available": True,
    },
]

def recommend_staff(ticket, tickets, staff_members=None):
    """Recommend an available specialist with the lowest workload."""

    if staff_members is None:
        staff_members = STAFF_MEMBERS

    category = ticket.get("category", "")

    if not isinstance(category, str) or not category.strip():
        raise ValueError("Please provide a ticket category.")

    category = category.strip().lower()

    candidates = [
        staff
        for staff in staff_members
        if staff.get("speciality", "").strip().lower() == category
        and staff.get("available") is True
    ]

    if not candidates:
        return None

    workloads = {
        staff["name"]: 0
        for staff in candidates
    }

    for current_ticket in tickets:
        if current_ticket.get("status") not in {"resolved", "closed"}:
            assignee = current_ticket.get("assigned_to")

            if assignee in workloads:
                workloads[assignee] += 1

    return min(
        candidates,
        key=lambda staff: workloads[staff["name"]],
    )