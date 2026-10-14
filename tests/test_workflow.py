import unittest
from unittest.mock import patch

from campusflow.tickets import create_ticket
from campusflow.workflow import update_ticket_status
from campusflow.workflow import assign_ticket, find_ticket, update_ticket_status


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "Network issue", "Network", "medium", 4)

    def test_find_ticket_is_case_insensitive(self):
        self.assertIs(find_ticket(self.tickets, "t001"), self.tickets[0])

    def test_missing_ticket_raises(self):
        with self.assertRaises(ValueError):
            find_ticket(self.tickets, "T999")

    def test_assign_ticket(self):
        with patch(
            "campusflow.workflow.STAFF_MEMBERS",
            [{"name": "Ada", "speciality": "Network", "available": True}],
        ):
            ticket = assign_ticket(self.tickets, "T001", "  Ada  ")

        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_assignment_is_recorded_in_history(self):
        with patch(
            "campusflow.workflow.STAFF_MEMBERS",
            [{"name": "John", "speciality": "Network", "available": True}],
        ):
            ticket = assign_ticket(self.tickets, "T001", "John")

        self.assertEqual(ticket["assigned_to"], "John")
        self.assertTrue(ticket["history"])
        self.assertEqual(ticket["history"][-1]["action"], "assigned")

    def test_status_change_is_recorded_in_history(self):
        tickets = []

        create_ticket(
            tickets,
            "Campus Wi-Fi outage",
            "Network",
            "high",
            12,
        )

        ticket = update_ticket_status(tickets, "T001", "in_progress")

        self.assertEqual(ticket["status"], "in_progress")
        self.assertEqual(len(ticket["history"]), 1)
        self.assertEqual(
        ticket["history"][0]["action"],
        "status_changed",
        )
        self.assertEqual(
            ticket["history"][0]["details"],
            "Status changed from open to in_progress",
        )
        self.assertIn("timestamp", ticket["history"][0])

    def test_blank_assignee_is_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", " ")

    def test_cannot_assign_closed_ticket(self):
        update_ticket_status(self.tickets, "T001", "closed")
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "Ada")

    def test_update_status_normalizes_case(self):
        ticket = update_ticket_status(self.tickets, "T001", " IN_PROGRESS ")
        self.assertEqual(ticket["status"], "in_progress")

    def test_invalid_status_is_rejected(self):
        with self.assertRaises(ValueError):
            update_ticket_status(self.tickets, "T001", "pending")


if __name__ == "__main__":
    unittest.main()
