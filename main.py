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


if __name__ == "__main__":
    manager = EmergencyManager(MapService.from_json(MAP))
    demo(manager) if "--demo" in sys.argv else console.run(manager)
