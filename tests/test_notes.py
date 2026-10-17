
"""Tests for adding and validating ticket notes."""

import unittest

from campusflow.notes import make_note_adder


class NoteTests(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Wi-Fi outage",
                "category": "Network",
                "urgency": "high",
                "affected_users": 15,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
                "notes": [],
            },
            {
                "id": "T002",
                "title": "Laptop fault",
                "category": "Hardware",
                "urgency": "medium",
                "affected_users": 2,
                "priority": "medium",
                "status": "open",
                "assigned_to": None,
                "notes": [
                    {
                        "note_id": "N004",
                        "author": "Ada",
                        "message": "Already investigated.",
                    }
                ],
            },
        ]

        self.add_note = make_note_adder(self.tickets)

    def test_add_note_to_ticket(self):
        note = self.add_note(
            "T001",
            "Myles",
            "Wi-Fi issue investigated.",
        )

        self.assertEqual(note["note_id"], "N005")
        self.assertEqual(note["author"], "Myles")
        self.assertEqual(
            note["message"],
            "Wi-Fi issue investigated.",
        )
        self.assertEqual(len(self.tickets[0]["notes"]), 1)

    def test_note_id_continues_across_tickets(self):
        note = self.add_note(
            "T001",
            "Myles",
            "Checking the router.",
        )

        self.assertEqual(note["note_id"], "N005")

    def test_unknown_ticket_is_rejected_without_changes(self):
        before = [
            {
                **ticket,
                "notes": [dict(note) for note in ticket["notes"]],
            }
            for ticket in self.tickets
        ]

        with self.assertRaises(ValueError):
            self.add_note(
                "T999",
                "Myles",
                "A useful note.",
            )

        self.assertEqual(self.tickets, before)

    def test_empty_author_is_rejected(self):
        before = [
            {
                **ticket,
                "notes": [dict(note) for note in ticket["notes"]],
            }
            for ticket in self.tickets
        ]

        with self.assertRaises(ValueError):
            self.add_note(
                "T001",
                "   ",
                "A useful note.",
            )

        self.assertEqual(self.tickets, before)

    def test_empty_message_is_rejected(self):
        before = [
            {
                **ticket,
                "notes": [dict(note) for note in ticket["notes"]],
            }
            for ticket in self.tickets
        ]

        with self.assertRaises(ValueError):
            self.add_note(
                "T001",
                "Myles",
                "   ",
            )

        self.assertEqual(self.tickets, before)


if __name__ == "__main__":
    unittest.main()
