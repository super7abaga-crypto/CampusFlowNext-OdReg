from campusflow.workflow import get_priority_queue

tickets = [
    {
        "id": "T003",
        "title": "Login failure",
        "priority": "medium",
        "status": "open",
    },
    {
        "id": "T002",
        "title": "Faulty keyboard",
        "priority": "low",
        "status": "open",
    },
    {
        "id": "T004",
        "title": "Network failure",
        "priority": "critical",
        "status": "in_progress",
    },
    {
        "id": "T001",
        "title": "Wi-Fi outage",
        "priority": "critical",
        "status": "open",
    },
    {
        "id": "T005",
        "title": "Old printer issue",
        "priority": "high",
        "status": "resolved",
    },
]

queue = get_priority_queue(tickets)

for ticket in queue:
    print(ticket["id"], "|", ticket["title"], "|", ticket["priority"])