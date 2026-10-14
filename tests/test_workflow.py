import unittest
from unittest.mock import patch

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_ticket,
    find_ticket,
    update_ticket_status,
)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        """Create a fresh ticket for each test."""
        self.tickets = []

        create_ticket(
            self.tickets,
            "Network issue",
            "Network",
            "medium",
            4,
        )

    def test_find_ticket_is_case_insensitive(self):
        """Ticket lookup should ignore ID letter case."""
        self.assertIs(
            find_ticket(self.tickets, "t001"),
            self.tickets[0],
        )

    def test_missing_ticket_raises(self):
        """Looking up a missing ticket should raise an error."""
        with self.assertRaises(ValueError):
            find_ticket(self.tickets, "T999")

    def test_assign_ticket(self):
        """A valid available staff member can be assigned."""
        with patch(
            "campusflow.workflow.STAFF_MEMBERS",
            [
                {
                    "name": "Ada",
                    "speciality": "Network",
                    "available": True,
                }
            ],
        ):
            ticket = assign_ticket(
                self.tickets,
                "T001",
                "  Ada  ",
            )

        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_assignment_is_recorded_in_history(self):
        """Assigning a ticket should record the assignment."""
        with patch(
            "campusflow.workflow.STAFF_MEMBERS",
            [
                {
                    "name": "John",
                    "speciality": "Network",
                    "available": True,
                }
            ],
        ):
            ticket = assign_ticket(
                self.tickets,
                "T001",
                "John",
            )

        self.assertEqual(ticket["assigned_to"], "John")
        self.assertTrue(ticket["history"])
        self.assertEqual(
            ticket["history"][-1]["action"],
            "assigned",
        )

    def test_status_change_is_recorded_in_history(self):
        """Changing status should record the change."""
        with patch(
            "campusflow.workflow.STAFF_MEMBERS",
            [
                {
                    "name": "Mr. Odeh",
                    "speciality": "Network",
                    "available": True,
                }
            ],
        ):
            assign_ticket(
                self.tickets,
                "T001",
                "Mr. Odeh",
            )

        ticket = update_ticket_status(
            self.tickets,
            "T001",
            "in_progress",
        )

        self.assertEqual(ticket["status"], "in_progress")
        self.assertEqual(len(ticket["history"]), 2)

        self.assertEqual(
            ticket["history"][0]["action"],
            "assigned",
        )

        self.assertEqual(
            ticket["history"][1]["action"],
            "status_changed",
        )

        self.assertEqual(
            ticket["history"][1]["details"],
            "Status changed from open to in_progress",
        )

        self.assertIn(
            "timestamp",
            ticket["history"][1],
        )

    def test_blank_assignee_is_rejected(self):
        """An empty staff name should be rejected."""
        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets,
                "T001",
                " ",
            )

    def test_cannot_assign_closed_ticket(self):
        """A closed ticket should not be assignable."""
        update_ticket_status(
            self.tickets,
            "T001",
            "closed",
        )

        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets,
                "T001",
                "Ada",
            )

    def test_update_status_normalizes_case(self):
        """Status updates should ignore case and surrounding spaces."""
        with patch(
            "campusflow.workflow.STAFF_MEMBERS",
            [
                {
                    "name": "Ada",
                    "speciality": "Network",
                    "available": True,
                }
            ],
        ):
            assign_ticket(
                self.tickets,
                "T001",
                "Ada",
            )

        ticket = update_ticket_status(
            self.tickets,
            "T001",
            " IN_PROGRESS ",
        )

        self.assertEqual(ticket["status"], "in_progress")

    def test_unassigned_ticket_cannot_move_to_in_progress(self):
        """An unassigned ticket must remain open."""
        ticket = self.tickets[0]

        self.assertEqual(ticket["status"], "open")
        self.assertFalse(ticket.get("assigned_to"))

        with self.assertRaisesRegex(
            ValueError,
            "assigned to a staff member",
        ):
            update_ticket_status(
                self.tickets,
                "T001",
                "in_progress",
            )

        self.assertEqual(ticket["status"], "open")

    def test_invalid_status_is_rejected(self):
        """An unsupported status should be rejected."""
        with self.assertRaises(ValueError):
            update_ticket_status(
                self.tickets,
                "T001",
                "pending",
            )


if __name__ == "__main__":
    unittest.main()