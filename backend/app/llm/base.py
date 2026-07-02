from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SummaryProvider(ABC):
    @abstractmethod
    def summarize(self, payload: dict[str, Any]) -> str:
        """Return a DevOps summary for a readiness payload."""
