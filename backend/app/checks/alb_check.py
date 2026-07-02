from __future__ import annotations

from ..aws.elbv2_client import Elbv2ReadonlyClient
from ..core.models import CheckResult, CheckStatus, Mode, ReadinessRequest, Severity


def run(request: ReadinessRequest) -> CheckResult:
    path = request.alb_health_check_path
    if not path.startswith("/"):
        return CheckResult(
            name="ALB Health Check Path Valid",
            status=CheckStatus.FAIL,
            severity=Severity.MEDIUM,
            evidence=f"ALB health check path {path} does not start with /.",
            recommendation="Use an absolute path such as /health.",
        )

    status = CheckStatus.PASS
    evidence = f"ALB health check path is {path}."
    recommendation = "Keep the ALB target group path aligned with the application health endpoint."
    if path == "/":
        status = CheckStatus.WARN
        recommendation = "Prefer a dedicated health endpoint such as /health for production services."

    if request.mode == Mode.AWS_READONLY and request.target_group_arn:
        client = Elbv2ReadonlyClient(region=request.aws_region, profile=request.aws_profile)
        exists, aws_path, message = client.target_group_health_path(request.target_group_arn)
        if not exists:
            return CheckResult(
                name="ALB Health Check Path Valid",
                status=CheckStatus.WARN,
                severity=Severity.MEDIUM,
                evidence=message,
                recommendation="Confirm the target group ARN and health check path before attaching ECS service traffic.",
            )
        if aws_path != path:
            return CheckResult(
                name="ALB Health Check Path Valid",
                status=CheckStatus.WARN,
                severity=Severity.MEDIUM,
                evidence=f"Provided path {path}; AWS target group path is {aws_path}.",
                recommendation="Align the requested ALB health check path with the existing target group configuration.",
            )
        evidence = f"Target group health check path matches AWS configuration: {aws_path}."

    return CheckResult(
        name="ALB Health Check Path Valid",
        status=status,
        severity=Severity.MEDIUM,
        evidence=evidence,
        recommendation=recommendation,
    )
