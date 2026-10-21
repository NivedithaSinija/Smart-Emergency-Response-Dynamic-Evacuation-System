import random
import unittest

from structures.bplus_tree import BPlusTree, DuplicateKeyError
from services.incident_store import IncidentStore


class TestBPlusTree(unittest.TestCase):
    def test_empty(self):
        t = BPlusTree()
        self.assertIsNone(t.search(1))
        self.assertEqual(t.range_query(0, 10), [])
        self.assertEqual(len(t), 0)

    def test_duplicate(self):
        t = BPlusTree()
        t.insert(1, "a")
        with self.assertRaises(DuplicateKeyError):
            t.insert(1, "b")

    def test_splits_and_search(self):
        t = BPlusTree(order=3)
        keys = list(range(200))
        random.Random(1).shuffle(keys)
        for k in keys:
            t.insert(k, k * 2)
        self.assertFalse(t.root.leaf)
        self.assertTrue(all(t.search(k) == k * 2 for k in keys))
        self.assertEqual([k for k, _ in t.items()], sorted(keys))
        self.assertEqual([k for k, _ in t.range_query(10, 15)], [10, 11, 12, 13, 14, 15])

    def test_delete_update(self):
        t = BPlusTree()
        for k in range(20):
            t.insert(k, k)
        self.assertTrue(t.delete(5))
        self.assertFalse(t.delete(5))
        self.assertIsNone(t.search(5))
        self.assertTrue(t.update(6, "x"))
        self.assertEqual(t.search(6), "x")
        self.assertEqual(len(t), 19)

    def test_store(self):
        s = IncidentStore()
        a = s.add("fire", "Library", 3)
        s.update_status(a.id, "responding")
        self.assertEqual(s.get(a.id).status, "responding")
        with self.assertRaises(ValueError):
            s.add("fire", "Library", 9)


class TestIncidentStoreQueries(unittest.TestCase):
    def setUp(self):
        self.s = IncidentStore(order=3)          # small order -> many splits
        for sev in [3, 5, 1, 4, 2, 5, 3, 1, 4, 2]:
            self.s.add("fire", "Library", sev)

    def test_id_range(self):
        self.assertEqual([i.id for i in self.s.range(3, 6)], [3, 4, 5, 6])
        self.assertEqual(self.s.range(50, 60), [])
        self.assertEqual(self.s.range(6, 3), [])

    def test_severity_range_sorted(self):
        got = self.s.by_severity(4, 5)
        self.assertEqual([(i.severity, i.id) for i in got], [(4, 4), (4, 9), (5, 2), (5, 6)])
        self.assertEqual(len(self.s.by_severity()), 10)

    def test_severity_index_follows_updates(self):
        self.s.update_severity(1, 5)             # was 3
        self.assertIn(1, [i.id for i in self.s.by_severity(5, 5)])
        self.assertNotIn(1, [i.id for i in self.s.by_severity(3, 3)])
        self.s.remove(2)
        self.assertNotIn(2, [i.id for i in self.s.by_severity(5, 5)])
        self.assertIsNone(self.s.get(2))
        self.assertEqual(len(self.s), 9)

    def test_status_update_visible_in_both_indexes(self):
        self.s.update_status(2, "resolved")
        self.assertEqual(self.s.get(2).status, "resolved")
        self.assertEqual([i for i in self.s.by_severity(5, 5) if i.id == 2][0].status, "resolved")
        self.assertNotIn(2, [i.id for i in self.s.active()])

    def test_missing_and_duplicate(self):
        with self.assertRaises(KeyError):
            self.s.update_status(999, "resolved")
        with self.assertRaises(DuplicateKeyError):
            self.s.add("fire", "Library", 2, incident_id=3)
        self.assertEqual(len(self.s), 10)        # failed add left no trace
        self.assertEqual(len(self.s.by_severity()), 10)


if __name__ == "__main__":
    unittest.main()
