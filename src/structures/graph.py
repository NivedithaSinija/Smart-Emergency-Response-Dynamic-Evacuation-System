class Edge:
    def __init__(self, a, b, base_cost):
        self.a, self.b = a, b
        self.base_cost = base_cost
        self.congestion = 1.0   # multiplier >= 1
        self.blocked = False

    @property
    def cost(self):
        return self.base_cost * self.congestion


class Graph:
    """Undirected weighted graph. Vertices have a kind: building/junction/exit."""

    def __init__(self):
        self.kinds = {}   # name -> kind
        self.adj = {}     # name -> {neighbour: Edge}
        self.meta = {}    # name -> dict (e.g. {"available": True} for exits)

    def add_vertex(self, name, kind="junction", **meta):
        if name in self.kinds:
            raise ValueError(f"vertex exists: {name}")
        self.kinds[name] = kind
        self.adj[name] = {}
        self.meta[name] = dict(meta)

    def has_vertex(self, name):
        return name in self.kinds

    def remove_vertex(self, name):
        for nb in list(self.adj.get(name, {})):
            del self.adj[nb][name]
        self.adj.pop(name, None)
        self.kinds.pop(name, None)
        self.meta.pop(name, None)

    def add_edge(self, a, b, cost):
        if a not in self.kinds or b not in self.kinds:
            raise KeyError("both vertices must exist")
        if cost < 0:
            raise ValueError("cost must be non-negative")
        e = Edge(a, b, cost)
        self.adj[a][b] = e
        self.adj[b][a] = e

    def get_edge(self, a, b):
        e = self.adj.get(a, {}).get(b)
        if e is None:
            raise KeyError(f"no corridor {a}-{b}")
        return e

    def remove_edge(self, a, b):
        self.get_edge(a, b)
        del self.adj[a][b]
        del self.adj[b][a]

    def set_blocked(self, a, b, blocked=True):
        self.get_edge(a, b).blocked = blocked

    def set_congestion(self, a, b, factor):
        if factor < 1:
            raise ValueError("congestion factor must be >= 1")
        self.get_edge(a, b).congestion = factor

    def neighbors(self, name):
        """Yield (neighbour, cost) over passable corridors."""
        for nb, e in self.adj[name].items():
            if not e.blocked:
                yield nb, e.cost

    def exits(self):
        return [n for n, k in self.kinds.items() if k == "exit"]
