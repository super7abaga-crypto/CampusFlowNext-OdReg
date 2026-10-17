from campusflow.storage import save_tickets, load_tickets

tickets = [
    {
        "id": "T001",
        "title": "Wi-Fi outage",
        "category": "Network",
        "urgency": "high",
        "affected_users": 15,
        "priority": "critical",
        "status": "open",
        "assigned_to": None,
    }
]

save_tickets(tickets, "test_tickets.json")

loaded_tickets = load_tickets("test_tickets.json")

print(loaded_tickets)
print("Storage test passed:", loaded_tickets == tickets)