
import unittest
from unittest.mock import patch

from campusflow.workflow import assign_ticket


class TestAssignTicket(unittest.TestCase):

    def setUp(self):
        self.staff = [
            {
                "name": "Mr. Odeh",
                "speciality": "Network",
                "available": True,
            },
            {
                "name": "Ms. Chijioke",
                "speciality": "Network",
                "available": True,
            },
            {
                "name": "Mr. Wealth",
                "speciality": "Other",
                "available": False,
            },
        ]

        self.ticket = {
            "id": "T001",
            "title": "Wi-Fi is not working",
            "category": "Network",
            "urgency": "high",
            "affected_users": 12,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
            "history": [],
        }

        self.tickets = [self.ticket]

        # Use a controlled staff list so the tests are predictable.
        self.staff_patcher = patch(
            "campusflow.workflow.STAFF_MEMBERS",
            self.staff,
        )
        self.staff_patcher.start()
        self.addCleanup(self.staff_patcher.stop)

    def test_assign_ticket_to_valid_staff_member(self):
        result = assign_ticket(
            self.tickets, "T001", "Mr. Odeh"
        )

        self.assertEqual(result["assigned_to"], "Mr. Odeh")
        self.assertTrue(result["history"])
        self.assertEqual(
            result["history"][-1]["action"].lower(),
            "assigned",
        )

    def test_reassign_ticket_to_another_staff_member(self):
        self.ticket["assigned_to"] = "Mr. Odeh"

        result = assign_ticket(
            self.tickets, "T001", "Ms. Chijioke"
        )

        self.assertEqual(
            result["assigned_to"], "Ms. Chijioke"
        )
        self.assertEqual(
            result["history"][-1]["action"].lower(),
            "reassigned",
        )
        self.assertIn(
            "Mr. Odeh",
            result["history"][-1]["details"],
        )
        self.assertIn(
            "Ms. Chijioke",
            result["history"][-1]["details"],
        )

    def test_empty_staff_name_is_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", " ")

        self.assertIsNone(self.ticket["assigned_to"])

    def test_unknown_staff_name_is_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets, "T001", "Mr. Unknown"
            )

        self.assertIsNone(self.ticket["assigned_to"])

    def test_unavailable_staff_member_is_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets, "T001", "Mr. Wealth"
            )

        self.assertIsNone(self.ticket["assigned_to"])

    def test_same_staff_cannot_be_assigned_twice(self):
        self.ticket["assigned_to"] = "Mr. Odeh"
        original_history = list(self.ticket["history"])

        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets, "T001", "Mr. Odeh"
            )

        self.assertEqual(
            self.ticket["assigned_to"], "Mr. Odeh"
        )
        self.assertEqual(
            self.ticket["history"], original_history
        )

    def test_resolved_ticket_cannot_be_reassigned(self):
        self.ticket["status"] = "resolved"
        self.ticket["assigned_to"] = "Mr. Odeh"

        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets, "T001", "Ms. Chijioke"
            )

        self.assertEqual(
            self.ticket["assigned_to"], "Mr. Odeh"
        )

    def test_closed_ticket_cannot_be_reassigned(self):
        self.ticket["status"] = "closed"
        self.ticket["assigned_to"] = "Mr. Odeh"

        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets, "T001", "Ms. Chijioke"
            )

        self.assertEqual(
            self.ticket["assigned_to"], "Mr. Odeh"
        )


if __name__ == "__main__":
    unittest.main()
