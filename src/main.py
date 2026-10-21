import os
import sys

from services.emergency_manager import EmergencyManager
from services.map_service import MapService
from ui import console

MAP = os.path.join(os.path.dirname(__file__), "data", "campus_map.json")


def demo(m):
    steps = [
        ("Initial route for Alice at Library", lambda: None),
        ("Fire (sev 5) reported at North Junction", lambda: m.report_incident("fire", "North Junction", 5)),
        ("Corridor Main Junction-Main Gate blocked", lambda: m.set_corridor_blocked("Main Junction", "Main Gate")),
        ("Sports Ground closed as shelter", lambda: m.set_shelter_available("Sports Ground", False)),
    ]
    for title, action in steps:
        print(f"\n## {title}")
        action()
        console.show_route(*m.get_route("Alice", "Library"))

    print("\n## B+ Tree queries on the incident database")
    for kind, loc, sev in [("smoke", "Cafeteria", 2), ("flood", "Hostel A", 3), ("gas leak", "Science Block", 4)]:
        m.report_incident(kind, loc, sev)
    print("-- IDs 2..4 (range query on primary index):")
    console.show_incidents(m.incidents_in_range(2, 4))
    print("-- severity 4..5 (range query on severity index):")
    console.show_incidents(m.incidents_by_severity(4, 5))


if __name__ == "__main__":
    manager = EmergencyManager(MapService.from_json(MAP))
    demo(manager) if "--demo" in sys.argv else console.run(manager)
