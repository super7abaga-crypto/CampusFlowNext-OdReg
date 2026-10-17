
import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import save_tickets, load_tickets


class TestTicketPersistence(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.filepath = Path(self.temp_dir.name) / "tickets.json"

        self.ticket = {
            "id": "T001",
            "title": "Wi-Fi is not working",
            "category": "Network",
            "urgency": "high",
            "affected_users": 12,
            "priority": "critical",
            "status": "in_progress",
            "assigned_to": "Mr. Odeh",
            "created_at": "2026-10-16T09:00:00",
            "history": [
                {
                    "action": "assigned",
                    "details": "Assigned to Mr. Odeh",
                    "timestamp": "2026-10-16T09:05:00",
                },
                {
                    "action": "status_changed",
                    "details": "Status changed to in_progress",
                    "timestamp": "2026-10-16T09:10:00",
                },
            ],
            "notes": [
                {
                    "note_id": "N001",
                    "author": "Engineer B",
                    "message": "Checked the network connection.",
                }
            ],
        }

    def test_save_and_reload_preserves_ticket_data(self):
        save_tickets([self.ticket], self.filepath)

        loaded = load_tickets(self.filepath)

        self.assertEqual(loaded, [self.ticket])

    def test_assignment_survives_reload(self):
        save_tickets([self.ticket], self.filepath)

        loaded = load_tickets(self.filepath)

        self.assertEqual(loaded[0]["assigned_to"], "Mr. Odeh")

    def test_history_and_timestamps_survive_reload(self):
        save_tickets([self.ticket], self.filepath)

        loaded = load_tickets(self.filepath)
        restored = loaded[0]

        self.assertEqual(
            restored["history"], self.ticket["history"]
        )
        self.assertEqual(
            restored["created_at"], self.ticket["created_at"]
        )

    def test_notes_survive_reload(self):
        save_tickets([self.ticket], self.filepath)

        loaded = load_tickets(self.filepath)

        self.assertEqual(loaded[0]["notes"], self.ticket["notes"])

    def test_missing_file_returns_empty_list(self):
        loaded = load_tickets(self.filepath)

        self.assertEqual(loaded, [])

    def test_corrupted_json_raises_error_without_erasing_file(self):
        corrupted_content = '{"tickets": [this is not valid JSON'
        self.filepath.write_text(corrupted_content, encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            load_tickets(self.filepath)

        self.assertEqual(
            self.filepath.read_text(encoding="utf-8"),
            corrupted_content,
        )

    def test_json_object_instead_of_list_is_rejected(self):
        self.filepath.write_text(
            json.dumps({"id": "T001"}),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "JSON list"):
            load_tickets(self.filepath)

    def test_duplicate_ticket_ids_are_rejected(self):
        duplicate_tickets = [self.ticket.copy(), self.ticket.copy()]
        save_tickets(duplicate_tickets, self.filepath)

        with self.assertRaisesRegex(ValueError, "Duplicate ticket ID"):
            load_tickets(self.filepath)

    def test_invalid_priority_is_rejected(self):
        invalid_ticket = self.ticket.copy()
        invalid_ticket["priority"] = "low"
        save_tickets([invalid_ticket], self.filepath)

        with self.assertRaisesRegex(ValueError, "incorrect priority"):
            load_tickets(self.filepath)

    def test_temporary_file_is_cleaned_up_after_save(self):
        save_tickets([self.ticket], self.filepath)

        temporary_path = self.filepath.with_suffix(
            self.filepath.suffix + ".tmp"
        )

        self.assertTrue(self.filepath.exists())
        self.assertFalse(temporary_path.exists())


if __name__ == "__main__":
    unittest.main()
