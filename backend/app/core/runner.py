from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from ..checks import (
    alb_check,
    cloudwatch_check,
    dependency_check,
    docker_image_check,
    ecr_check,
    env_var_check,
    health_check,
    iam_role_check,
    port_check,
    secret_scan_check,
    task_size_check,
)
from ..llm.ollama_client import generate_summary
from .models import CheckResult, Mode, ReadinessReport, ReadinessRequest
from .scoring import calculate_score, determine_final_status


def _report_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}-{uuid4().hex[:8]}"


def run_readiness_check(request: ReadinessRequest) -> ReadinessReport:
    checks: list[CheckResult] = []
    if request.mode == Mode.AWS_READONLY:
        checks.append(ecr_check.run(request))
    else:
        checks.append(docker_image_check.run(request))

    checks.extend(
        [
            port_check.run(request),
            health_check.run(request),
            env_var_check.run(request),
            dependency_check.run(request),
            task_size_check.run(request),
            secret_scan_check.run(request),
            cloudwatch_check.run(request),
            iam_role_check.run(request),
            alb_check.run(request),
        ]
    )
    score_summary = calculate_score(checks)
    final_status = determine_final_status(score_summary)
    summary_payload = {
        "final_status": final_status.value,
        "score": score_summary.score,
        "checks": [check.model_dump(mode="json") for check in checks],
        "input": request.model_dump(mode="json"),
    }
    ai_summary, provider, warning = generate_summary(summary_payload)
    return ReadinessReport(
        report_id=_report_id(),
        input=request,
        checks=checks,
        score_summary=score_summary,
        final_status=final_status,
        ai_summary=ai_summary,
        ai_summary_provider=provider,
        ai_summary_warning=warning,
    )
