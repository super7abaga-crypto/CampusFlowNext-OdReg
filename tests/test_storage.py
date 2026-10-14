import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import load_tickets, save_tickets


class StorageTests(unittest.TestCase):
    def test_missing_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(load_tickets(Path(directory) / "missing.json"), [])

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
    }
]
            save_tickets(tickets, path)
            self.assertEqual(load_tickets(path), tickets)

    def test_invalid_json_raises_value_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text("not json", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_tickets(path)

    def test_non_list_json_raises_value_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text(json.dumps({"id": "T001"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_tickets(path)

    def test_list_item_without_string_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text(json.dumps([{"title": "No ID"}]), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_tickets(path)


if __name__ == "__main__":
    unittest.main()
