
import unittest

from campusflow.staff import recommend_staff, STAFF_MEMBERS


class TestStaffRecommendationEdges(unittest.TestCase):

    def test_staff_with_three_active_tickets_is_not_recommended(self):
        staff = [
            {
                "name": "Mr. Odeh",
                "speciality": "Network",
                "available": True,
            }
        ]

        tickets = [
            {"id": "T001", "status": "open", "assigned_to": "Mr. Odeh"},
            {"id": "T002", "status": "open", "assigned_to": "Mr. Odeh"},
            {
                "id": "T003",
                "status": "in_progress",
                "assigned_to": "Mr. Odeh",
            },
        ]

        ticket = {"id": "T004", "category": "Network"}

        result = recommend_staff(ticket, tickets, staff)

        self.assertIsNone(result)

    def test_kingsley_workload_counts_across_specialities(self):
        kingsley_network = {
            "name": "Mr. Kingsley (HOC)",
            "speciality": "Network",
            "available": True,
        }

        tickets = [
            {
                "id": "T001",
                "category": "Network",
                "status": "open",
                "assigned_to": "Mr. Kingsley (HOC)",
            },
            {
                "id": "T002",
                "category": "Software",
                "status": "in_progress",
                "assigned_to": "Mr. Kingsley",
            },
            {
                "id": "T003",
                "category": "Network",
                "status": "open",
                "assigned_to": "Mr. Kingsley (HOC)",
            },
        ]

        ticket = {"id": "T004", "category": "Network"}

        result = recommend_staff(
            ticket, tickets, [kingsley_network]
        )

        self.assertIsNone(result)

    def test_busy_specialists_are_skipped_for_next_available_person(self):
        tickets = [
            # Mr. Odeh has three active tickets.
            {"id": "T001", "status": "open", "assigned_to": "Mr. Odeh"},
            {"id": "T002", "status": "open", "assigned_to": "Mr. Odeh"},
            {
                "id": "T003",
                "status": "in_progress",
                "assigned_to": "Mr. Odeh",
            },

            # Kingsley has three active tickets across both specialities.
            {
                "id": "T004",
                "category": "Network",
                "status": "open",
                "assigned_to": "Mr. Kingsley (HOC)",
            },
            {
                "id": "T005",
                "category": "Software",
                "status": "open",
                "assigned_to": "Mr. Kingsley (HOC)",
            },
            {
                "id": "T006",
                "category": "Network",
                "status": "in_progress",
                "assigned_to": "Mr. Kingsley",
            },
        ]

        ticket = {"id": "T007", "category": "Network"}

        result = recommend_staff(ticket, tickets, STAFF_MEMBERS)

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Ms. Chijioke")

    def test_resolved_tickets_do_not_count_as_active_workload(self):
        staff = [
            {
                "name": "Mr. Odeh",
                "speciality": "Network",
                "available": True,
            }
        ]

        tickets = [
            {
                "id": "T001",
                "status": "resolved",
                "assigned_to": "Mr. Odeh",
            },
            {
                "id": "T002",
                "status": "closed",
                "assigned_to": "Mr. Odeh",
            },
        ]

        ticket = {"id": "T003", "category": "Network"}

        result = recommend_staff(ticket, tickets, staff)

        self.assertEqual(result["name"], "Mr. Odeh")


if __name__ == "__main__":
    unittest.main()
