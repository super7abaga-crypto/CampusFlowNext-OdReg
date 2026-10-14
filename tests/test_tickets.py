import unittest

from campusflow.tickets import calculate_priority, create_ticket, generate_ticket_id, validate_ticket_details
from campusflow.tickets import create_ticket

class PriorityTests(unittest.TestCase):
    def test_critical_for_high_and_ten_users(self):
        self.assertEqual(calculate_priority("high", 10), "critical")

    def test_critical_for_high_and_more_than_ten_users(self):
        self.assertEqual(calculate_priority("high", 25), "critical")

    def test_high_for_high_urgency_with_few_users(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_high_for_ten_users_with_low_urgency(self):
        self.assertEqual(calculate_priority("low", 10), "high")

    def test_medium_for_medium_urgency(self):
        self.assertEqual(calculate_priority("medium", 1), "medium")

    def test_medium_for_three_users(self):
        self.assertEqual(calculate_priority("low", 3), "medium")

    def test_low_for_low_urgency_and_one_user(self):
        self.assertEqual(calculate_priority("low", 1), "low")

    def test_priority_normalizes_urgency(self):
        self.assertEqual(calculate_priority(" HIGH ", 1), "high")

    def test_invalid_urgency_raises(self):
        with self.assertRaises(ValueError):
            calculate_priority("urgent", 1)

    def test_invalid_affected_users_raises(self):
        for value in (0, -1, 2.5, "3", True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                calculate_priority("low", value)
            
def test_new_ticket_has_creation_timestamp(self):
    tickets = []

    ticket = create_ticket(
        tickets,
        "Campus Wi-Fi outage",
        "Network",
        "high",
        12,
    )

    self.assertIn("created_at", ticket)
    self.assertTrue(ticket["created_at"])


class TicketCreationTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []

    def test_creates_ticket_with_expected_defaults(self):
        ticket = create_ticket(self.tickets, "Wi-Fi is down", "network", "high", 12)
        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["title"], "Wi-Fi is down")
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["affected_users"], 12)
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])
        self.assertEqual(len(self.tickets), 1)

    def test_title_is_trimmed(self):
        ticket = create_ticket(self.tickets, "  Printer broken  ", "Hardware", "low", 1)
        self.assertEqual(ticket["title"], "Printer broken")

    def test_ids_increment(self):
        create_ticket(self.tickets, "First", "Other", "low", 1)
        second = create_ticket(self.tickets, "Second", "Other", "low", 1)
        self.assertEqual(second["id"], "T002")

    def test_id_uses_highest_existing_number(self):
        self.assertEqual(generate_ticket_id([{"id": "T002"}, {"id": "T010"}]), "T011")

    def test_blank_title_is_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "   ", "Other", "low", 1)

    def test_invalid_category_is_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "Issue", "Food", "low", 1)

    def test_invalid_urgency_is_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "Issue", "Other", "urgent", 1)

    def test_invalid_affected_users_is_rejected(self):
        for value in (0, -2, 1.5, "2", True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_ticket_details("Issue", "Other", "low", value)


if __name__ == "__main__":
    unittest.main()
