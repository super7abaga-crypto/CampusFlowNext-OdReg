import unittest
from unittest.mock import patch

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_ticket,
    find_ticket,
    update_ticket_status,
    search_tickets,
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

        ticket = find_ticket(self.tickets, "T001")

        # Assign the ticket before closing it.
        ticket["assigned_to"] = "Mr. Odeh"

        update_ticket_status(
            self.tickets,
            "T001",
            "closed",
        )

        original_assignee = ticket["assigned_to"]

        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets,
                "T001",
                "Ada",
            )

        # Confirm that the failed operation did not change the assignment.
        self.assertEqual(
            ticket["assigned_to"],
            original_assignee,
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

    def test_unassigned_ticket_cannot_be_resolved(self):
        with self.assertRaises(ValueError):
            update_ticket_status(
                self.tickets,
                "T001",
                "resolved",
            )

        self.assertEqual(
            find_ticket(self.tickets, "T001")["status"],
            "open",
        )


    def test_unassigned_ticket_cannot_be_closed(self):
        with self.assertRaises(ValueError):
            update_ticket_status(
                self.tickets,
                "T001",
                "closed",
            )

        self.assertEqual(
            find_ticket(self.tickets, "T001")["status"],
            "open",
        )


    def test_resolved_ticket_cannot_be_reassigned(self):
        ticket = find_ticket(self.tickets, "T001")
        ticket["status"] = "resolved"
        ticket["assigned_to"] = "Mr. Odeh"

        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets,
                "T001",
                "Ada",
            )

        self.assertEqual(ticket["assigned_to"], "Mr. Odeh")


    def test_closed_ticket_cannot_be_reassigned(self):
        ticket = find_ticket(self.tickets, "T001")
        ticket["status"] = "closed"
        ticket["assigned_to"] = "Mr. Odeh"

        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets,
                "T001",
                "Ada",
            )

        self.assertEqual(ticket["assigned_to"], "Mr. Odeh")

    def test_invalid_status_is_rejected(self):
        """An unsupported status should be rejected."""
        with self.assertRaises(ValueError):
            update_ticket_status(
                self.tickets,
                "T001",
                "pending",
            )

    def test_search_tickets_matches_partial_title(self):
        """Search should match part of a ticket title."""
        create_ticket(
            self.tickets,
            "Network cable damaged",
            "Network",
            "high",
            2,
        )

        results = search_tickets(
            self.tickets,
            "cable",
            None,
            None,
            None,
            None,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Network cable damaged")

    def test_search_tickets_is_case_insensitive(self):
        """Search should ignore capitalization."""
        create_ticket(
            self.tickets,
            "Network connection is slow",
            "Network",
            "high",
            3,
        )

        results = search_tickets(
            self.tickets,
            "NETWORK",
            None,
            None,
            None,
            None,
        )

        self.assertEqual(len(results), 2)

    def test_search_tickets_combines_keyword_and_status(self):
        """Search should apply title and status filters together."""
        create_ticket(
            self.tickets,
            "Network cable damaged",
            "Network",
            "high",
            2,
        )

        results = search_tickets(
            self.tickets,
            "network",
            "open",
            None,
            None,
            None,
        )

        self.assertEqual(len(results), 2)
        self.assertTrue(
            all(ticket["status"] == "open" for ticket in results)
        )

    def test_search_tickets_empty_keyword_returns_filtered_tickets(self):
        """A whitespace-only keyword should skip title matching."""
        results = search_tickets(
            self.tickets,
            "   ",
            None,
            None,
            None,
            None,
        )

        self.assertEqual(results, self.tickets)

    def test_search_tickets_none_keyword_returns_filtered_tickets(self):
        """A None keyword should skip title matching."""
        results = search_tickets(
            self.tickets,
            None,
            None,
            None,
            None,
            None,
        )

        self.assertEqual(results, self.tickets)

    def test_search_tickets_no_match_returns_empty_list(self):
        """A keyword absent from all titles should return no results."""
        results = search_tickets(
            self.tickets,
            "printer",
            None,
            None,
            None,
            None,
        )

        self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main()