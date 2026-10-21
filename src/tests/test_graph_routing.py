import os
import unittest

from algorithms.evacuation import find_evacuation_route
from services.map_service import MapService

MAP = os.path.join(os.path.dirname(__file__), "..", "data", "campus_map.json")


class TestRouting(unittest.TestCase):
    def setUp(self):
        self.m = MapService.from_json(MAP)
        self.g = self.m.graph

    def test_basic_route(self):
        r = find_evacuation_route(self.g, "Admin Block")
        self.assertEqual(r["exit"], "Main Gate")
        self.assertEqual(r["cost"], 60)

    def test_blocked_corridor_reroutes(self):
        self.m.block_corridor("Main Junction", "Main Gate")
        r = find_evacuation_route(self.g, "Admin Block")
        self.assertNotEqual(r["exit"], "Main Gate")

    def test_unsafe_vertex_excluded(self):
        r = find_evacuation_route(self.g, "Library", unsafe={"North Junction"})
        self.assertNotIn("North Junction", r["route"])

    def test_congestion_changes_cost(self):
        before = find_evacuation_route(self.g, "Cafeteria")["cost"]
        self.m.set_congestion("Cafeteria", "Main Junction", 10)
        self.assertGreater(find_evacuation_route(self.g, "Cafeteria")["cost"], before)

    def test_no_route(self):
        for e in self.g.exits():
            self.m.set_exit_available(e, False)
        self.assertIsNone(find_evacuation_route(self.g, "Library"))

    def test_remove(self):
        self.g.remove_edge("Admin Block", "Main Junction")
        self.assertFalse("Main Junction" in self.g.adj["Admin Block"])
        self.g.remove_vertex("Cafeteria")
        self.assertFalse(self.g.has_vertex("Cafeteria"))
