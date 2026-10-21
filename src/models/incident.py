from dataclasses import dataclass, field
from datetime import datetime

STATUSES = ("reported", "responding", "contained", "resolved")


@dataclass
class Incident:
    id: int
    kind: str          # e.g. fire, flood, gas leak
    location: str      # vertex name on the campus map
    severity: int      # 1 (minor) .. 5 (critical)
    status: str = "reported"
    created: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))

    @property
    def active(self):
        return self.status != "resolved"
