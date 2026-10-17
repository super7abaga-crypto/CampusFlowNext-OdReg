
"""Tests for ticket JSON storage and note validation."""

import json
import tempfile
import unittest
from pathlib import Path

from campusflow.notes import make_note_adder
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket


class StorageTests(unittest.TestCase):
    def test_missing_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.json"
            self.assertEqual(load_tickets(path), [])

    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "tickets.json"

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
                    "notes": [],
                }
            ]

            save_tickets(tickets, path)
            loaded_tickets = load_tickets(path)

            self.assertEqual(loaded_tickets, tickets)

    def test_invalid_json_raises_value_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text("not json", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_tickets(path)

    def test_non_list_json_raises_value_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text(
                json.dumps({"id": "T001"}),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_tickets(path)

    def test_list_item_without_string_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text(
                json.dumps([{"title": "No ID"}]),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_tickets(path)

    def test_invalid_note_author_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"

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
                    "notes": [
                        {
                            "note_id": "N001",
                            "author": "   ",
                            "message": "Router checked.",
                        }
                    ],
                }
            ]

            path.write_text(json.dumps(tickets), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_tickets(path)

    def test_invalid_note_message_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"

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
                    "notes": [
                        {
                            "note_id": "N001",
                            "author": "Myles",
                            "message": "   ",
                        }
                    ],
                }
            ]

            path.write_text(json.dumps(tickets), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_tickets(path)

    def test_duplicate_note_ids_across_tickets_are_rejected(self):
        """Reject the same note ID appearing on different tickets."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"

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
                    "notes": [
                        {
                            "note_id": "N001",
                            "author": "Myles",
                            "message": "First ticket note.",
                        }
                    ],
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
                            "note_id": "N001",
                            "author": "Ada",
                            "message": "Second ticket note.",
                        }
                    ],
                },
            ]

            path.write_text(json.dumps(tickets), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_tickets(path)

    def test_duplicate_note_ids_are_rejected(self):
        """Reject duplicate note IDs on the same ticket."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"

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
                    "notes": [
                        {
                            "note_id": "N001",
                            "author": "Myles",
                            "message": "First note.",
                        },
                        {
                            "note_id": "N001",
                            "author": "Ada",
                            "message": "Second note.",
                        },
                    ],
                }
            ]

            path.write_text(json.dumps(tickets), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_tickets(path)

    def test_ticket_and_note_ids_continue_after_reload(self):
        """IDs continue correctly after tickets are saved and reloaded."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"

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
                    "notes": [
                        {
                            "note_id": "N004",
                            "author": "Myles",
                            "message": "Router checked.",
                        }
                    ],
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
                    "notes": [],
                },
            ]

            save_tickets(tickets, path)
            loaded_tickets = load_tickets(path)

            # The next ticket ID should follow T002.
            new_ticket = create_ticket(
                loaded_tickets,
                "Broken keyboard",
                "Hardware",
                "low",
                1,
            )
            self.assertEqual(new_ticket["id"], "T003")

            # Bind the note function to the loaded collection.
            add_note = make_note_adder(loaded_tickets)

            new_note = add_note(
                "T001",
                "Ada",
                "The router has been checked again.",
            )
            self.assertEqual(new_note["note_id"], "N005")

            # Save and reload to confirm the records persist.
            save_tickets(loaded_tickets, path)
            reloaded_tickets = load_tickets(path)

            self.assertEqual(len(reloaded_tickets), 3)
            self.assertEqual(reloaded_tickets[2]["id"], "T003")
            self.assertEqual(
                reloaded_tickets[0]["notes"][-1]["note_id"],
                "N005",
            )


if __name__ == "__main__":
    unittest.main()
