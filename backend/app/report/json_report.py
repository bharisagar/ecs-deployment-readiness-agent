from __future__ import annotations

from ..core.models import ReadinessReport

def render_json(report: ReadinessReport) -> str:
    return report.model_dump_json(indent=2, by_alias=True)


