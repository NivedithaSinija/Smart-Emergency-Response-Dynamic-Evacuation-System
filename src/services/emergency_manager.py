from algorithms.evacuation import find_evacuation_route
from services.incident_store import IncidentStore
from services.map_service import MapService

DANGER_SEVERITY = 4  # active incidents at/above this make their location unsafe


class EmergencyManager:
    def __init__(self, map_service: MapService, store: IncidentStore = None):
        self.map = map_service
        self.store = store or IncidentStore()
        self.log = []            # human-readable change events
        self._last = {}          # person -> (route dict, log index when computed)

    # ---- state changes ----
    def unsafe_areas(self):
        return {i.location for i in self.store.active() if i.severity >= DANGER_SEVERITY}

    def report_incident(self, kind, location, severity):
        if not self.map.graph.has_vertex(location):
            raise ValueError(f"unknown location: {location}")
        inc = self.store.add(kind, location, severity)
        self.log.append(f"{kind} reported at {location} (severity {severity})")
        return inc

    def update_severity(self, incident_id, severity):
        inc = self.store.update_severity(incident_id, severity)
        self.log.append(f"incident #{incident_id} at {inc.location} severity -> {severity}")
        return inc

    def update_status(self, incident_id, status):
        inc = self.store.update_status(incident_id, status)
        self.log.append(f"incident #{incident_id} at {inc.location} status -> {status}")
        return inc

    def set_corridor_blocked(self, a, b, blocked=True):
        self.map.block_corridor(a, b, blocked)
        self.log.append(f"corridor {a}-{b} {'blocked' if blocked else 'reopened'}")

    def set_congestion(self, a, b, factor):
        self.map.set_congestion(a, b, factor)
        self.log.append(f"corridor {a}-{b} congestion x{factor}")

    def set_shelter_available(self, exit_name, available):
        self.map.set_exit_available(exit_name, available)
        self.log.append(f"exit {exit_name} {'available' if available else 'unavailable'}")

    # ---- incident queries (B+ Tree range queries) ----
    def incidents_in_range(self, low, high):
        return self.store.range(low, high)

    def incidents_by_severity(self, min_severity, max_severity=5):
        return self.store.by_severity(min_severity, max_severity)

    # ---- routing ----
    def get_route(self, person, location):
        """Returns (result_or_None, explanation)."""
        result = find_evacuation_route(self.map.graph, location, self.unsafe_areas())
        prev = self._last.get(person)
        changes = self.log[prev[1]:] if prev else []
        self._last[person] = (result, len(self.log))
        if result is None:
            return None, "No safe route to any available exit. Shelter in place and call for help."
        if prev is None:
            return result, "Initial route: lowest-cost path to the nearest safe exit."
        old = prev[0]
        if old and old["route"] == result["route"]:
            return result, "Route unchanged."
        why = "; ".join(changes) if changes else "network conditions changed"
        return result, f"Route changed because: {why}."
