from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..core.config import REPORTS_DIR
from ..core.models import ArtifactPaths, ReadinessReport
from ..report.json_report import render_json
from ..report.markdown_report import render_markdown


class LocalReportStore:
    def __init__(self, reports_dir: Path = REPORTS_DIR) -> None:
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def save(self, report: ReadinessReport) -> ReadinessReport:
        markdown_path = self.reports_dir / f"readiness-report-{report.report_id}.md"
        json_path = self.reports_dir / f"readiness-report-{report.report_id}.json"
        report.artifacts = ArtifactPaths(markdown=str(markdown_path), json_path=str(json_path))
        markdown_path.write_text(render_markdown(report), encoding="utf-8")
        json_path.write_text(render_json(report), encoding="utf-8")
        return report

    def get(self, report_id: str) -> ReadinessReport | None:
        path = self.reports_dir / f"readiness-report-{report_id}.json"
        if not path.exists():
            return None
        return ReadinessReport.model_validate_json(path.read_text(encoding="utf-8"))

    def list_reports(self) -> list[dict[str, Any]]:
        reports: list[dict[str, Any]] = []
        for path in sorted(self.reports_dir.glob("readiness-report-*.json"), reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            reports.append(
                {
                    "report_id": payload.get("report_id"),
                    "created_at": payload.get("created_at"),
                    "image": payload.get("input", {}).get("image"),
                    "mode": payload.get("input", {}).get("mode"),
                    "final_status": payload.get("final_status"),
                    "score": payload.get("score_summary", {}).get("score"),
                    "passed": payload.get("score_summary", {}).get("passed"),
                    "warnings": payload.get("score_summary", {}).get("warnings"),
                    "failed": payload.get("score_summary", {}).get("failed"),
                }
            )
        return reports

