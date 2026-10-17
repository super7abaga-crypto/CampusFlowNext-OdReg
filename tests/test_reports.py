import unittest

from campusflow.reports import format_report, format_ticket, summarize_tickets


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {"id": "T001", "title": "Wi-Fi", "category": "Network", "urgency": "high", "affected_users": 12, "priority": "critical", "status": "open", "assigned_to": None},
            {"id": "T002", "title": "Mouse", "category": "Hardware", "urgency": "low", "affected_users": 1, "priority": "low", "status": "resolved", "assigned_to": "Ada"},
        ]

    def test_summary_counts_groups_and_unassigned(self):
        report = summarize_tickets(self.tickets)
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["by_status"], {"open": 1, "resolved": 1})
        self.assertEqual(report["by_priority"], {"critical": 1, "low": 1})
        self.assertEqual(report["by_category"], {"Network": 1, "Hardware": 1})
        self.assertEqual(report["unassigned"], 1)
        self.assertEqual(report["unresolved"], 1)
        self.assertEqual(report["resolved"], 1)
        self.assertEqual(report["resolution_percentage"], 50.0)

    def test_format_ticket_includes_core_details(self):
        line = format_ticket(self.tickets[0])
        self.assertIn("T001", line)
        self.assertIn("Wi-Fi", line)
        self.assertIn("critical", line)
        self.assertIn("Unassigned", line)

    def test_format_report_includes_total_and_unassigned(self):
        report = format_report(self.tickets)
        self.assertIn("2 total ticket(s)", report)
        self.assertIn("Unassigned tickets: 1", report)
        self.assertIn("Unresolved tickets: 1", report)
        self.assertIn("Resolved tickets: 1", report)
        self.assertIn("Resolution percentage: 50.00%", report)
        self.assertIn("Reopened tickets: 0", report)

    def test_empty_report_is_readable(self):
        report = format_report([])
        self.assertIn("0 total ticket(s)", report)
        self.assertIn("None", report)

    def test_reopened_tickets_count_each_ticket_once(self):
        tickets = [
            {
                "id": "T001",
                "history": [
                    {
                        "action": "status_changed",
                        "details": "Status changed from resolved to open",
                    },
                    {
                        "action": "status_changed",
                        "details": "Status changed from resolved to open",
                    },
                ],
            },
            {
                "id": "T002",
                "history": [
                    {
                        "action": "status_changed",
                        "details": "Status changed from resolved to open",
                    },
                ],
            },
        ]

        report = summarize_tickets(tickets)
        self.assertEqual(report["reopened"], 2)


if __name__ == "__main__":
    unittest.main()
