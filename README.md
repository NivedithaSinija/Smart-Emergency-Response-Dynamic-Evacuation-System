# Smart-Emergency-Response-Dynamic-Evacuation-System
A Python-based emergency simulation that uses a B+ Tree for incident management, Graph ADT to represent pathways, and Dijkstra’s algorithm to calculate safe evacuation routes. It dynamically updates routes based on hazards and blocked paths to improve emergency response efficiency.

Data-structures project: B+ Tree incident database, weighted-graph campus map,
Dijkstra routing with a heap priority queue, and a console interface.

## Setup
Python 3.8+ only, no external dependencies.

    git clone <your-repo-url> && cd <repo>
    python main.py --demo     # scripted end-to-end demo
    python main.py            # interactive menu
    python -m unittest discover -s tests -t .   # run all tests

## Layout / ownership
| Person | Files |
|---|---|
| 1 | structures/bplus_tree.py, models/incident.py, services/incident_store.py |
| 2 | structures/graph.py, services/map_service.py, data/campus_map.json |
| 3 | algorithms/dijkstra.py, algorithms/evacuation.py, structures/priority_queue.py |
| 4 | main.py, services/emergency_manager.py, ui/console.py, tests/test_integration.py |

## Behaviour notes
- Incidents with severity >= 4 that are not resolved make their location unsafe; routes avoid it.
- Blocked corridors are skipped; congestion multiplies a corridor's cost.
- Exits can be marked unavailable (shelter closed).
- B+ Tree deletion is lazy (no rebalancing): correct, but leaves may become sparse.
- Each route request explains what changed since that person's last route.
