from __future__ import annotations

from typing import Any

from .base import SummaryProvider


class RuleBasedSummaryProvider(SummaryProvider):
    def summarize(self, payload: dict[str, Any]) -> str:
        checks = payload.get("checks", [])
        final_status = payload.get("final_status", "UNKNOWN")
        score = payload.get("score", 0)
        failed = [check for check in checks if check.get("status") == "FAIL"]
        warnings = [check for check in checks if check.get("status") == "WARN"]
        high_failures = [check for check in failed if check.get("severity") == "HIGH"]

        lines = [
            f"Overall deployment readiness: {final_status} with a score of {score}%.",
            "",
            "Top risks:",
        ]
        if high_failures:
            for check in high_failures[:5]:
                lines.append(f"- HIGH: {check['name']} failed. Evidence: {check['evidence']}")
        elif failed:
            for check in failed[:5]:
                lines.append(f"- {check['severity']}: {check['name']} failed. Evidence: {check['evidence']}")
        elif warnings:
            for check in warnings[:5]:
                lines.append(f"- {check['severity']}: {check['name']} needs attention. Evidence: {check['evidence']}")
        else:
            lines.append("- No blocking readiness risks were found.")

        lines.extend(["", "Recommended next actions:"])
        actionable = failed + warnings
        if actionable:
            for check in actionable[:6]:
                lines.append(f"- {check['recommendation']}")
        else:
            lines.append("- Proceed to peer review and infrastructure change approval using immutable image tags.")

        lines.extend(
            [
                "",
                "Interview-style explanation:",
                (
                    "This agent behaves like a pre-deployment quality gate for ECS/Fargate. "
                    "It validates image availability, runtime configuration, observability, IAM, "
                    "health checks, and secret hygiene before any service is created, reducing failed "
                    "deployments and avoiding unnecessary AWS spend."
                ),
            ]
        )
        return "\n".join(lines)
