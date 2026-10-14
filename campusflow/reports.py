"""Summary and display helpers for ticket collections."""


def summarize_tickets(tickets):
    """Return totals grouped by status, priority, and category."""
    report = {
        "total": len(tickets),
        "by_status": {},
        "by_priority": {},
        "by_category": {},
        "unassigned": 0,
    }
    for ticket in tickets:
        for key, field in (("by_status", "status"), ("by_priority", "priority"), ("by_category", "category")):
            value = ticket.get(field, "unknown")
            report[key][value] = report[key].get(value, 0) + 1
        if not ticket.get("assigned_to"):
            report["unassigned"] += 1
    return report


def format_ticket(ticket):
    """Format a ticket with creation time and activity history."""

    from datetime import datetime

    created_at = ticket.get("created_at", "Not recorded")

    if created_at != "Not recorded":
        try:
            timestamp = datetime.fromisoformat(created_at)
            created_at = timestamp.strftime("%d-%m-%Y %I:%M:%S %p")
        except (ValueError, TypeError):
            pass

    lines = [
        f"{ticket['id']} | "
        f"{ticket['title']} | "
        f"{ticket['category']} | "
        f"urgency: {ticket['urgency']} | "
        f"priority: {ticket['priority']} | "
        f"status: {ticket['status']} | "
        f"affected users: {ticket['affected_users']} | "
        f"assigned to: {ticket.get('assigned_to') or 'Unassigned'} | "
        f"created at: {created_at}"
    ]

    history = ticket.get("history", [])

    if history:
        lines.append("")
        lines.append("History:")

        for event in history:
            timestamp = event.get("timestamp", "Unknown time")

            try:
                timestamp = datetime.fromisoformat(timestamp)
                timestamp = timestamp.strftime("%d-%m-%Y %I:%M:%S %p")
            except (ValueError, TypeError):
                pass

            action = event.get("action", "Unknown action")
            details = event.get("details", "")

            lines.append(
                f"  {timestamp} | "
                f"{ticket['id']} | "
                f"{action} | "
                f"{details}"
            )

    return "\n".join(lines)


def format_report(tickets):
    """Return a human-readable summary report."""
    report = summarize_tickets(tickets)
    lines = [f"Ticket report — {report['total']} total ticket(s)"]
    for title, key in (("By status", "by_status"), ("By priority", "by_priority"), ("By category", "by_category")):
        lines.append(f"{title}:")
        if report[key]:
            lines.extend(f"  - {name}: {count}" for name, count in sorted(report[key].items()))
        else:
            lines.append("  - None")
    lines.append(f"Unassigned tickets: {report['unassigned']}")
    return "\n".join(lines)
