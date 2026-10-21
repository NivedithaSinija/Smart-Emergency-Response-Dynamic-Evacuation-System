from models.incident import Incident, STATUSES
from structures.bplus_tree import BPlusTree

MAX_KEY = float("inf")


class IncidentStore:
    """Incident database built on two B+ Trees.

    primary index   : incident ID            -> Incident   (ID order == report order)
    secondary index : (severity, incident ID) -> Incident   (for severity range queries)
    Both support fast point lookups AND range queries via the linked leaves.
    """

    def __init__(self, order=4):
        self._tree = BPlusTree(order)       # key: id
        self._by_sev = BPlusTree(order)     # key: (severity, id)
        self._next_id = 1

    @staticmethod
    def _check_severity(severity):
        if not 1 <= severity <= 5:
            raise ValueError("severity must be 1-5")

    def _require(self, incident_id):
        inc = self.get(incident_id)
        if inc is None:
            raise KeyError(incident_id)
        return inc

    # ---- create / read ----
    def add(self, kind, location, severity, incident_id=None):
        self._check_severity(severity)
        if incident_id is None:
            incident_id = self._next_id
        inc = Incident(incident_id, kind, location, severity)
        self._tree.insert(incident_id, inc)            # raises DuplicateKeyError
        self._by_sev.insert((severity, incident_id), inc)
        self._next_id = max(self._next_id, incident_id + 1)
        return inc

    def get(self, incident_id):
        return self._tree.search(incident_id)

    # ---- updates ----
    def update_status(self, incident_id, status):
        if status not in STATUSES:
            raise ValueError(f"status must be one of {STATUSES}")
        inc = self._require(incident_id)
        inc.status = status
        self._tree.update(incident_id, inc)
        self._by_sev.update((inc.severity, incident_id), inc)
        return inc

    def update_severity(self, incident_id, severity):
        self._check_severity(severity)
        inc = self._require(incident_id)
        if severity != inc.severity:
            # the secondary key changes, so move the entry
            self._by_sev.delete((inc.severity, incident_id))
            inc.severity = severity
            self._by_sev.insert((severity, incident_id), inc)
        return inc

    def remove(self, incident_id):
        inc = self.get(incident_id)
        if inc is None:
            return False
        self._tree.delete(incident_id)
        self._by_sev.delete((inc.severity, incident_id))
        return True

    # ---- range queries (the reason a B+ Tree is used) ----
    def range(self, low, high):
        """Incidents with low <= ID <= high, in ID order.  O(log n + k)."""
        return [v for _, v in self._tree.range_query(low, high)]

    def by_severity(self, min_severity=1, max_severity=5):
        """Incidents with min <= severity <= max, ordered by severity then ID.
        O(log n + k) using the secondary index."""
        self._check_severity(min_severity)
        self._check_severity(max_severity)
        return [v for _, v in self._by_sev.range_query((min_severity, 0), (max_severity, MAX_KEY))]

    def all(self):
        return [v for _, v in self._tree.items()]

    def active(self):
        return [i for i in self.all() if i.active]

    def __len__(self):
        return len(self._tree)
