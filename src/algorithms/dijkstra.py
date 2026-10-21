from structures.priority_queue import PriorityQueue


def dijkstra(graph, start, unsafe=frozenset()):
    """Shortest costs from start. Skips blocked corridors and unsafe vertices
    (the start vertex is always allowed). Returns (dist, prev)."""
    if not graph.has_vertex(start):
        raise KeyError(f"unknown location: {start}")
    dist, prev = {start: 0}, {}
    pq = PriorityQueue()
    pq.push(start, 0)
    done = set()
    while pq:
        u, d = pq.pop()
        if u in done:
            continue
        done.add(u)
        for v, cost in graph.neighbors(u):
            if v in unsafe:
                continue
            nd = d + cost
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                pq.push(v, nd)
    return dist, prev


def build_path(prev, start, target):
    path = [target]
    while path[-1] != start:
        path.append(prev[path[-1]])
    return path[::-1]
