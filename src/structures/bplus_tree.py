"""B+ Tree: sorted key -> value map with linked leaves for fast range queries."""
from bisect import bisect_left, bisect_right


class DuplicateKeyError(KeyError):
    pass


class _Node:
    def __init__(self, leaf):
        self.leaf = leaf
        self.keys = []
        self.children = []  # internal nodes: child nodes
        self.values = []    # leaf nodes: stored values
        self.next = None    # leaf nodes: next leaf


class BPlusTree:
    def __init__(self, order=4):
        if order < 3:
            raise ValueError("order must be >= 3")
        self.max_keys = order - 1
        self.root = _Node(leaf=True)
        self._size = 0

    def __len__(self):
        return self._size

    def __contains__(self, key):
        return self.search(key) is not None

    # ---- insertion ----
    def insert(self, key, value):
        """Insert key; raises DuplicateKeyError if it already exists."""
        res = self._insert(self.root, key, value)
        if res:
            sep, right = res
            root = _Node(leaf=False)
            root.keys = [sep]
            root.children = [self.root, right]
            self.root = root
        self._size += 1

    def _insert(self, node, key, value):
        if node.leaf:
            i = bisect_left(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key:
                raise DuplicateKeyError(key)
            node.keys.insert(i, key)
            node.values.insert(i, value)
            if len(node.keys) <= self.max_keys:
                return None
            mid = len(node.keys) // 2
            right = _Node(leaf=True)
            right.keys, right.values = node.keys[mid:], node.values[mid:]
            node.keys, node.values = node.keys[:mid], node.values[:mid]
            right.next, node.next = node.next, right
            return right.keys[0], right
        i = bisect_right(node.keys, key)
        res = self._insert(node.children[i], key, value)
        if not res:
            return None
        sep, right_child = res
        node.keys.insert(i, sep)
        node.children.insert(i + 1, right_child)
        if len(node.keys) <= self.max_keys:
            return None
        mid = len(node.keys) // 2
        up = node.keys[mid]
        right = _Node(leaf=False)
        right.keys, right.children = node.keys[mid + 1:], node.children[mid + 1:]
        node.keys, node.children = node.keys[:mid], node.children[:mid + 1]
        return up, right

    # ---- lookup ----
    def _find_leaf(self, key):
        node = self.root
        while not node.leaf:
            node = node.children[bisect_right(node.keys, key)]
        return node

    def search(self, key):
        """Return the value for key, or None."""
        leaf = self._find_leaf(key)
        i = bisect_left(leaf.keys, key)
        if i < len(leaf.keys) and leaf.keys[i] == key:
            return leaf.values[i]
        return None

    def update(self, key, value):
        leaf = self._find_leaf(key)
        i = bisect_left(leaf.keys, key)
        if i < len(leaf.keys) and leaf.keys[i] == key:
            leaf.values[i] = value
            return True
        return False

    def range_query(self, low, high):
        """All (key, value) with low <= key <= high, in order."""
        out = []
        leaf = self._find_leaf(low)
        while leaf:
            for k, v in zip(leaf.keys, leaf.values):
                if k > high:
                    return out
                if k >= low:
                    out.append((k, v))
            leaf = leaf.next
        return out

    def items(self):
        node = self.root
        while not node.leaf:
            node = node.children[0]
        while node:
            yield from zip(node.keys, node.values)
            node = node.next

    # ---- deletion (lazy: no rebalancing; tree stays correct, may be sparse) ----
    def delete(self, key):
        leaf = self._find_leaf(key)
        i = bisect_left(leaf.keys, key)
        if i < len(leaf.keys) and leaf.keys[i] == key:
            leaf.keys.pop(i)
            leaf.values.pop(i)
            self._size -= 1
            return True
        return False
