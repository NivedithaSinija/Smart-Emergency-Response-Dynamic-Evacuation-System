import os
import unittest

from services.emergency_manager import EmergencyManager
from services.map_service import MapService

MAP = os.path.join(os.path.dirname(__file__), "..", "data", "campus_map.json")


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.m = EmergencyManager(MapService.from_json(MAP))

    def test_end_to_end_reroute_with_explanation(self):
        r1, why1 = self.m.get_route("alice", "Library")
        self.assertIn("Initial", why1)
        self.m.report_incident("fire", "North Junction", 5)
        r2, why2 = self.m.get_route("alice", "Library")
        self.assertNotIn("North Junction", r2["route"])
        self.assertIn("fire reported at North Junction", why2)
        self.assertNotEqual(r1["route"], r2["route"])

    def test_low_severity_does_not_close_area(self):
        inc = self.m.report_incident("smoke", "North Junction", 2)
        self.assertEqual(self.m.unsafe_areas(), set())
        self.m.update_severity(inc.id, 5)
        self.assertEqual(self.m.unsafe_areas(), {"North Junction"})
        self.m.update_status(inc.id, "resolved")
        self.assertEqual(self.m.unsafe_areas(), set())

    def test_shelter_unavailable_and_no_route(self):
        for e in self.m.map.graph.exits():
            self.m.set_shelter_available(e, False)
        r, why = self.m.get_route("bob", "Hostel A")
        self.assertIsNone(r)
        self.assertIn("No safe route", why)

    def test_unchanged_route(self):
        self.m.get_route("c", "Admin Block")
        _, why = self.m.get_route("c", "Admin Block")
        self.assertEqual(why, "Route unchanged.")

    def test_bad_location(self):
        with self.assertRaises(ValueError):
            self.m.report_incident("fire", "Mars", 3)


if __name__ == "__main__":
    unittest.main()
