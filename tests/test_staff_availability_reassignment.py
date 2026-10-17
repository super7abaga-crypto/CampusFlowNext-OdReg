
import unittest

from campusflow.staff import recommend_staff


class TestStaffAvailabilityAndReassignment(unittest.TestCase):

    def setUp(self):
        self.staff = [
            {
                "name": "Mr. Odeh",
                "speciality": "Network",
                "available": True,
            },
            {
                "name": "Ms. Chijioke",
                "speciality": "Network",
                "available": True,
            },
        ]

    def test_unavailable_staff_is_not_recommended(self):
        staff = [
            {
                "name": "Mr. Odeh",
                "speciality": "Network",
                "available": False,
            },
            {
                "name": "Ms. Chijioke",
                "speciality": "Network",
                "available": True,
            },
        ]

        ticket = {"id": "T001", "category": "Network"}

        result = recommend_staff(ticket, [], staff)

        self.assertEqual(result["name"], "Ms. Chijioke")

    def test_no_recommendation_when_all_specialists_unavailable(self):
        staff = [
            {
                "name": "Mr. Odeh",
                "speciality": "Network",
                "available": False,
            },
            {
                "name": "Ms. Chijioke",
                "speciality": "Network",
                "available": False,
            },
        ]

        ticket = {"id": "T001", "category": "Network"}

        result = recommend_staff(ticket, [], staff)

        self.assertIsNone(result)

    def test_reassignment_updates_recommended_staff(self):
        tickets = [
            {
                "id": "T001",
                "category": "Network",
                "status": "open",
                "assigned_to": "Mr. Odeh",
            }
        ]

        new_ticket = {"id": "T002", "category": "Network"}

        # Mr. Odeh has one active ticket, so Ms. Chijioke
        # should be recommended because her workload is zero.
        result = recommend_staff(new_ticket, tickets, self.staff)
        self.assertEqual(result["name"], "Ms. Chijioke")

        # Simulate T001 being reassigned to Ms. Chijioke.
        tickets[0]["assigned_to"] = "Ms. Chijioke"

        # Now Mr. Odeh has zero active tickets and should
        # be recommended instead.
        result = recommend_staff(new_ticket, tickets, self.staff)
        self.assertEqual(result["name"], "Mr. Odeh")


if __name__ == "__main__":
    unittest.main()
