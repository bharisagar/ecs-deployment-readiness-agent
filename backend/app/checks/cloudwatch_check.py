from __future__ import annotations

from ..aws.cloudwatch_client import CloudWatchReadonlyClient
from ..core.models import CheckResult, CheckStatus, Mode, ReadinessRequest, Severity


def run(request: ReadinessRequest) -> CheckResult:
    log_group = request.cloudwatch_log_group

    if request.mode == Mode.AWS_READONLY:
        if not log_group:
            return CheckResult(
                name="CloudWatch Log Group Configured",
                status=CheckStatus.FAIL,
                severity=Severity.MEDIUM,
                evidence="No CloudWatch log group name was provided.",
                recommendation="Provide an existing /ecs/<service> log group or create it through an approved IaC workflow.",
            )
        client = CloudWatchReadonlyClient(region=request.aws_region, profile=request.aws_profile)
        exists, message = client.log_group_exists(log_group)
        return CheckResult(
            name="CloudWatch Log Group Configured",
            status=CheckStatus.PASS if exists else CheckStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=message,
            recommendation="Ensure the ECS task definition awslogs configuration points to the intended log group.",
        )

    if not log_group:
        return CheckResult(
            name="CloudWatch Log Group Configured",
            status=CheckStatus.WARN,
            severity=Severity.MEDIUM,
            evidence="No CloudWatch log group name was provided in the request.",
            recommendation="Use a convention such as /ecs/<service-name> and provision it through Terraform/CDK.",
        )

    status = CheckStatus.PASS if log_group.startswith("/ecs/") else CheckStatus.WARN
    return CheckResult(
        name="CloudWatch Log Group Configured",
        status=status,
        severity=Severity.MEDIUM,
        evidence=f"Configured log group: {log_group}. Local mode validates naming only.",
        recommendation="In aws-readonly mode, the agent can confirm whether the log group already exists.",
    )
