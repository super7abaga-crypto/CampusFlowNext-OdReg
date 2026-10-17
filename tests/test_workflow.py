"""Tests for ticket assignment, status changes, and workflow protections."""

import unittest
from unittest.mock import patch

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_ticket,
    find_ticket,
    get_priority_queue,
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

    def assign_test_ticket(self):
        """Assign the test ticket to an available staff member."""
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
            return assign_ticket(
                self.tickets,
                "T001",
                "Mr. Odeh",
            )

    def close_test_ticket(self):
        """Close a ticket by following the valid status sequence."""
        ticket = find_ticket(self.tickets, "T001")
        ticket["assigned_to"] = "Mr. Odeh"

        update_ticket_status(self.tickets, "T001", "in_progress")
        update_ticket_status(self.tickets, "T001", "resolved")
        update_ticket_status(self.tickets, "T001", "closed")

        return ticket

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

    def test_priority_queue_contains_only_open_tickets(self):
        """The priority queue should contain open tickets only."""
        tickets = [
            {"id": "T001", "priority": "high", "status": "open"},
            {"id": "T002", "priority": "critical", "status": "open"},
            {
                "id": "T003",
                "priority": "critical",
                "status": "in_progress",
            },
            {"id": "T004", "priority": "high", "status": "resolved"},
            {"id": "T005", "priority": "low", "status": "open"},
            {"id": "T006", "priority": "medium", "status": "closed"},
        ]

        queue = get_priority_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in queue],
            ["T002", "T001", "T005"],
        )

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
        self.assertEqual(ticket["history"][-1]["action"], "assigned")

    def test_status_change_is_recorded_in_history(self):
        """Changing status should record the change."""
        self.assign_test_ticket()

        ticket = update_ticket_status(
            self.tickets,
            "T001",
            "in_progress",
        )

        self.assertEqual(ticket["status"], "in_progress")
        self.assertEqual(len(ticket["history"]), 2)
        self.assertEqual(ticket["history"][0]["action"], "assigned")
        self.assertEqual(ticket["history"][1]["action"], "status_changed")
        self.assertEqual(
            ticket["history"][1]["details"],
            "Status changed from open to in_progress",
        )
        self.assertIn("timestamp", ticket["history"][1])

    def test_blank_assignee_is_rejected(self):
        """An empty staff name should be rejected."""
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", " ")

    def test_cannot_assign_closed_ticket(self):
        """A closed ticket should not be assignable."""
        ticket = self.close_test_ticket()
        original_assignee = ticket["assigned_to"]

        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "Ada")

        self.assertEqual(ticket["assigned_to"], original_assignee)

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
            assign_ticket(self.tickets, "T001", "Ada")

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
            update_ticket_status(self.tickets, "T001", "in_progress")

        self.assertEqual(ticket["status"], "open")

    def test_unassigned_ticket_cannot_be_resolved(self):
        """An unassigned ticket cannot be resolved."""
        with self.assertRaises(ValueError):
            update_ticket_status(self.tickets, "T001", "resolved")

        self.assertEqual(
            find_ticket(self.tickets, "T001")["status"],
            "open",
        )

    def test_unassigned_ticket_cannot_be_closed(self):
        """An unassigned ticket cannot be closed."""
        with self.assertRaises(ValueError):
            update_ticket_status(self.tickets, "T001", "closed")

        self.assertEqual(
            find_ticket(self.tickets, "T001")["status"],
            "open",
        )

    def test_resolved_ticket_cannot_be_reassigned(self):
        """A resolved ticket cannot be reassigned."""
        ticket = find_ticket(self.tickets, "T001")
        ticket["status"] = "resolved"
        ticket["assigned_to"] = "Mr. Odeh"

        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "Ada")

        self.assertEqual(ticket["assigned_to"], "Mr. Odeh")

    def test_closed_ticket_cannot_be_reassigned(self):
        """A closed ticket cannot be reassigned."""
        ticket = self.close_test_ticket()
        original_assignee = ticket["assigned_to"]

        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "Ada")

        self.assertEqual(ticket["assigned_to"], original_assignee)

    def test_resolved_ticket_cannot_move_directly_to_in_progress(self):
        """A resolved ticket must be reopened before work resumes."""
        ticket = self.tickets[0]
        ticket["assigned_to"] = "Mr. Odeh"
        ticket["status"] = "resolved"

        with self.assertRaisesRegex(ValueError, "reopened to open"):
            update_ticket_status(
                self.tickets,
                "T001",
                "in_progress",
            )

        self.assertEqual(ticket["status"], "resolved")

    def test_resolved_ticket_can_be_reopened(self):
        """A resolved ticket can return to open."""
        ticket = self.tickets[0]
        ticket["assigned_to"] = "Mr. Odeh"
        ticket["status"] = "resolved"

        updated_ticket = update_ticket_status(
            self.tickets,
            "T001",
            "open",
        )

        self.assertEqual(updated_ticket["status"], "open")

    def test_reopened_ticket_can_move_to_in_progress(self):
        """A reopened, assigned ticket can resume work."""
        ticket = self.tickets[0]
        ticket["assigned_to"] = "Mr. Odeh"
        ticket["status"] = "resolved"

        update_ticket_status(self.tickets, "T001", "open")
        updated_ticket = update_ticket_status(
            self.tickets,
            "T001",
            "in_progress",
        )

        self.assertEqual(updated_ticket["status"], "in_progress")

    def test_invalid_status_is_rejected(self):
        """An unsupported status should be rejected."""
        with self.assertRaises(ValueError):
            update_ticket_status(self.tickets, "T001", "pending")

    # Regression tests for valid status transitions.

    def test_open_ticket_cannot_jump_to_closed(self):
        """An open ticket must enter in_progress before closing."""
        ticket = self.tickets[0]
        ticket["assigned_to"] = "Mr. Odeh"

        with self.assertRaisesRegex(ValueError, "in_progress"):
            update_ticket_status(self.tickets, "T001", "closed")

        self.assertEqual(ticket["status"], "open")

    def test_in_progress_ticket_cannot_jump_to_closed(self):
        """An in-progress ticket must be resolved before closing."""
        ticket = self.tickets[0]
        ticket["assigned_to"] = "Mr. Odeh"
        update_ticket_status(self.tickets, "T001", "in_progress")

        with self.assertRaisesRegex(ValueError, "resolved"):
            update_ticket_status(self.tickets, "T001", "closed")

        self.assertEqual(ticket["status"], "in_progress")

    def test_closed_ticket_cannot_move_to_in_progress(self):
        """A closed ticket must be reopened before work resumes."""
        ticket = self.close_test_ticket()

        with self.assertRaisesRegex(ValueError, "reopened to open"):
            update_ticket_status(self.tickets, "T001", "in_progress")

        self.assertEqual(ticket["status"], "closed")

    def test_closed_ticket_cannot_move_to_resolved(self):
        """A closed ticket cannot jump directly to resolved."""
        ticket = self.close_test_ticket()

        with self.assertRaisesRegex(ValueError, "reopened to open"):
            update_ticket_status(self.tickets, "T001", "resolved")

        self.assertEqual(ticket["status"], "closed")

    def test_closed_ticket_can_be_reopened(self):
        """A closed ticket can return to open."""
        ticket = self.close_test_ticket()

        updated_ticket = update_ticket_status(
            self.tickets,
            "T001",
            "open",
        )

        self.assertEqual(updated_ticket["status"], "open")
        self.assertEqual(ticket["status"], "open")

    def test_reopened_closed_ticket_can_resume_work(self):
        """A closed ticket can resume work after being reopened."""
        ticket = self.close_test_ticket()

        update_ticket_status(self.tickets, "T001", "open")
        updated_ticket = update_ticket_status(
            self.tickets,
            "T001",
            "in_progress",
        )

        self.assertEqual(updated_ticket["status"], "in_progress")
        self.assertEqual(ticket["status"], "in_progress")

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