from campusflow.workflow import filter_tickets

tickets = [
    {
        "id": "T001",
        "title": "Wi-Fi outage",
        "category": "Network",
        "priority": "critical",
        "status": "open",
        "assigned_to": "Peter",
    },
    {
        "id": "T002",
        "title": "Broken keyboard",
        "category": "Hardware",
        "priority": "low",
        "status": "open",
        "assigned_to": "Grace",
    },
    {
        "id": "T003",
        "title": "Login problem",
        "category": "Software",
        "priority": "medium",
        "status": "in_progress",
        "assigned_to": "Daniel",
    },
    {
        "id": "T004",
        "title": "Campus network failure",
        "category": "Network",
        "priority": "critical",
        "status": "resolved",
        "assigned_to": "Peter",
    },
]


print("OPEN TICKETS")
print(filter_tickets(tickets, status="open"))

print("\nCRITICAL TICKETS")
print(filter_tickets(tickets, priority="critical"))

print("\nNETWORK TICKETS")
print(filter_tickets(tickets, category="network"))

print("\nPETER'S TICKETS")
print(filter_tickets(tickets, assigned_to="peter"))

print("\nOPEN + CRITICAL")
print(filter_tickets(tickets, status="open", priority="critical"))