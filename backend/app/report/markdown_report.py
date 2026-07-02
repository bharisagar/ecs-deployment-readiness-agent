from __future__ import annotations

import json

from ..core.models import CheckStatus, ReadinessReport, Severity
from ..core.redaction import redact_text


def _status_line(status: CheckStatus) -> str:
    return {
        CheckStatus.PASS: "PASS",
        CheckStatus.WARN: "WARN",
        CheckStatus.FAIL: "FAIL",
    }[status]


def render_markdown(report: ReadinessReport) -> str:
    high_risk = [
        check
        for check in report.checks
        if check.severity == Severity.HIGH and check.status in {CheckStatus.FAIL, CheckStatus.WARN}
    ]
    recommendations = [
        check.recommendation
        for check in report.checks
        if check.status in {CheckStatus.FAIL, CheckStatus.WARN}
    ]

    lines = [
        "# ECS Deployment Readiness Report",
        "",
        "## 1. Executive Summary",
        "",
        f"Report ID: `{report.report_id}`",
        f"Generated at: `{report.created_at.isoformat()}`",
        f"Final status: **{report.final_status.value}**",
        "",
        "## 2. Overall Score",
        "",
        f"Score: **{report.score_summary.score}%**",
        f"Passed: {report.score_summary.passed}",
        f"Warnings: {report.score_summary.warnings}",
        f"Failed: {report.score_summary.failed}",
        "",
        "## 3. Final Status",
        "",
        f"**{report.final_status.value}**",
        "",
        "## 4. Input Configuration",
        "",
        "```json",
        json.dumps(report.input.model_dump(mode="json"), indent=2),
        "```",
        "",
        "## 5. Check Results",
        "",
    ]

    for check in report.checks:
        lines.extend(
            [
                f"### {check.name}",
                "",
                f"- Status: **{_status_line(check.status)}**",
                f"- Severity: **{check.severity.value}**",
                f"- Evidence: {check.evidence}",
                f"- Recommendation: {check.recommendation}",
                "",
            ]
        )

    lines.extend(["## 6. High-Risk Findings", ""])
    if high_risk:
        for check in high_risk:
            lines.append(f"- **{check.status.value}** {check.name}: {check.evidence}")
    else:
        lines.append("- No high-severity blocking findings.")

    lines.extend(["", "## 7. Recommendations", ""])
    if recommendations:
        for recommendation in dict.fromkeys(recommendations):
            lines.append(f"- {recommendation}")
    else:
        lines.append("- Proceed with normal deployment review and change approval.")

    lines.extend(
        [
            "",
            "## 8. AI DevOps Summary",
            "",
            report.ai_summary,
        ]
    )
    if report.ai_summary_warning:
        lines.extend(["", f"> {report.ai_summary_warning}"])

    lines.extend(
        [
            "",
            "## 9. Production Deployment Checklist",
            "",
            "- [ ] Use immutable image tag or digest",
            "- [ ] Configure required environment variables",
            "- [ ] Store secrets in AWS Secrets Manager or SSM Parameter Store",
            "- [ ] Confirm health endpoint and ALB target group path",
            "- [ ] Validate CloudWatch awslogs configuration",
            "- [ ] Validate ECS task execution role permissions",
            "- [ ] Confirm security groups and network reachability",
            "- [ ] Confirm rollback image tag",
            "",
            "## 10. Next Steps",
            "",
            "Review failed and warning checks, update the deployment configuration, then rerun the readiness check before creating or updating an ECS service.",
            "",
        ]
    )
    return redact_text("\n".join(lines))
