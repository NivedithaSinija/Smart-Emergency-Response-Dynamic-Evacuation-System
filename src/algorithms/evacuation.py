from algorithms.dijkstra import dijkstra, build_path


def find_evacuation_route(graph, start, unsafe=frozenset(), exits=None):
    """Cheapest route from start to a safe, available exit.
    Returns {"route", "cost", "exit"} or None if no exit is reachable."""
    if exits is None:
        exits = [e for e in graph.exits() if graph.meta[e].get("available", True)]
    exits = [e for e in exits if e not in unsafe]
    dist, prev = dijkstra(graph, start, unsafe)
    reachable = [e for e in exits if e in dist]
    if not reachable:
        return None
    best = min(reachable, key=lambda e: dist[e])
    return {"route": build_path(prev, start, best), "cost": dist[best], "exit": best}
