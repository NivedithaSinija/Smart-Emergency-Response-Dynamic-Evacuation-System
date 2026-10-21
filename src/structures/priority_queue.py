import heapq
from itertools import count


class PriorityQueue:
    """Min-heap; ties broken by insertion order so items are never compared."""

    def __init__(self):
        self._heap = []
        self._counter = count()

    def push(self, item, priority):
        heapq.heappush(self._heap, (priority, next(self._counter), item))

    def pop(self):
        priority, _, item = heapq.heappop(self._heap)
        return item, priority

    def __len__(self):
        return len(self._heap)

    def __bool__(self):
        return bool(self._heap)
