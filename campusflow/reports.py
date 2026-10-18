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

    open_status = report["by_status"].get("open", 0)
    in_progress_status = report["by_status"].get("in_progress", 0)
    unresolved_tickets = open_status + in_progress_status
    report["unresolved"] = unresolved_tickets
    resolved_status = report["by_status"].get("resolved", 0)
    report["resolved"] = resolved_status

    if report["total"] > 0:
        resolved_percentage = (resolved_status / report["total"]) * 100
        report["resolution_percentage"] = resolved_percentage
    else:
        report["resolution_percentage"] = 0

    reopened_count = 0
    for ticket in tickets:
        history = ticket.get("history", [])
        for history_entry in history:
            action = history_entry.get("action", "Unknown action")
            details = history_entry.get("details", "")
            if action == "status_changed" and "Status changed from resolved to open" in details:
                reopened_count += 1
                break  
    report["reopened"] = reopened_count
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

    BOLD = "\033[1m"
    RESET = "\033[0m"

    lines = [
        f"{BOLD}{ticket['id']}{RESET} | "
        f"{BOLD}{ticket['title']}{RESET} | "
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
        lines.append("\033[1mHistory:\033[0m")
      
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
                f"{ticket['id']:<6} | "
                f"{timestamp:<23} | "
                f"{action.replace('_', ' ').title():<16} | "
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
    lines.append(f"Unresolved tickets: {report['unresolved']}")
    lines.append(f"Resolved tickets: {report['resolved']}")
    lines.append(f"Resolution percentage: {report['resolution_percentage']:.2f}%")
    lines.append(f"Reopened tickets: {report['reopened']}")

    return "\n".join(lines)
