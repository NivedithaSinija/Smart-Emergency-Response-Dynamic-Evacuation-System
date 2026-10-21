import json
from structures.graph import Graph


class MapService:
    def __init__(self, graph=None):
        self.graph = graph or Graph()

    @classmethod
    def from_json(cls, path):
        with open(path) as f:
            data = json.load(f)
        g = Graph()
        for v in data["vertices"]:
            meta = {k: x for k, x in v.items() if k not in ("name", "kind")}
            g.add_vertex(v["name"], v["kind"], **meta)
        for a, b, cost in data["edges"]:
            g.add_edge(a, b, cost)
        return cls(g)

    def block_corridor(self, a, b, blocked=True):
        self.graph.set_blocked(a, b, blocked)

    def set_congestion(self, a, b, factor):
        self.graph.set_congestion(a, b, factor)

    def set_exit_available(self, name, available):
        if self.graph.kinds.get(name) != "exit":
            raise ValueError(f"{name} is not an exit")
        self.graph.meta[name]["available"] = available

    def available_exits(self):
        return [e for e in self.graph.exits() if self.graph.meta[e].get("available", True)]

    def corridors(self):
        seen, out = set(), []
        for a, nbrs in self.graph.adj.items():
            for b, e in nbrs.items():
                if id(e) not in seen:
                    seen.add(id(e))
                    out.append(e)
        return out
