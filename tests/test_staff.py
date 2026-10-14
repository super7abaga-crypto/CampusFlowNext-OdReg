import unittest

from campusflow.staff import recommend_staff
from campusflow.tickets import create_ticket


class StaffRecommendationTests(unittest.TestCase):

    def setUp(self):
        self.staff_members = [
            {
                "name": "John",
                "speciality": "Network",
                "available": True,
            },
            {
                "name": "Mary",
                "speciality": "Network",
                "available": True,
            },
            {
                "name": "David",
                "speciality": "Hardware",
                "available": False,
            },
        ]

        self.tickets = []

        self.ticket = create_ticket(
            self.tickets,
            "Campus Wi-Fi outage",
            "Network",
            "high",
            12,
        )

    def test_recommends_matching_specialist(self):
        recommendation = recommend_staff(
            self.ticket,
            self.tickets,
            self.staff_members,
        )

        self.assertIn(recommendation["name"], ["John", "Mary"])

    def test_prefers_specialist_with_lower_workload(self):
        self.tickets.extend([
            {
                "id": "T002",
                "assigned_to": "John",
                "status": "open",
            },
            {
                "id": "T003",
                "assigned_to": "John",
                "status": "in_progress",
            },
        ])

        recommendation = recommend_staff(
            self.ticket,
            self.tickets,
            self.staff_members,
        )

        self.assertEqual(recommendation["name"], "Mary")

    def test_skips_unavailable_staff(self):
        hardware_ticket = create_ticket(
            self.tickets,
            "Faulty laptop",
            "Hardware",
            "medium",
            2,
        )

        recommendation = recommend_staff(
            hardware_ticket,
            self.tickets,
            self.staff_members,
        )

        self.assertIsNone(recommendation)

    def test_returns_none_when_no_specialist_matches(self):
        other_ticket = create_ticket(
            self.tickets,
            "Other campus issue",
            "Other",
            "low",
            1,
        )

        recommendation = recommend_staff(
            other_ticket,
            self.tickets,
            self.staff_members,
        )

        self.assertIsNone(recommendation)


if __name__ == "__main__":
    unittest.main()