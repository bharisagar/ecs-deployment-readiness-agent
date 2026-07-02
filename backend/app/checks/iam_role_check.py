from __future__ import annotations

from ..aws.iam_client import IamReadonlyClient
from ..core.models import CheckResult, CheckStatus, Mode, ReadinessRequest, Severity


REQUIRED_POLICY_NAME = "AmazonECSTaskExecutionRolePolicy"


def run(request: ReadinessRequest) -> CheckResult:
    role_name = request.task_execution_role_name
    if request.mode == Mode.AWS_READONLY:
        if not role_name:
            return CheckResult(
                name="IAM Task Execution Role Valid",
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                evidence="No ECS task execution role name was provided.",
                recommendation="Provide a task execution role with AmazonECSTaskExecutionRolePolicy or equivalent permissions.",
            )
        client = IamReadonlyClient(region=request.aws_region, profile=request.aws_profile)
        exists, policies, message = client.execution_role_status(role_name)
        has_required_policy = any(REQUIRED_POLICY_NAME in policy for policy in policies)
        if exists and has_required_policy:
            return CheckResult(
                name="IAM Task Execution Role Valid",
                status=CheckStatus.PASS,
                severity=Severity.HIGH,
                evidence=f"Role {role_name} exists and includes {REQUIRED_POLICY_NAME}.",
                recommendation="Keep runtime permissions in a separate task role with least privilege.",
                metadata={"attached_policies": policies},
            )
        return CheckResult(
            name="IAM Task Execution Role Valid",
            status=CheckStatus.FAIL,
            severity=Severity.HIGH,
            evidence=message,
            recommendation=f"Attach {REQUIRED_POLICY_NAME} or an equivalent least-privilege policy before deployment.",
            metadata={"attached_policies": policies},
        )

    if role_name:
        return CheckResult(
            name="IAM Task Execution Role Valid",
            status=CheckStatus.PASS,
            severity=Severity.HIGH,
            evidence=f"Task execution role name is provided: {role_name}. Local mode does not call IAM.",
            recommendation="Run aws-readonly mode before approval to confirm the role and attached policies exist.",
        )

    return CheckResult(
        name="IAM Task Execution Role Valid",
        status=CheckStatus.FAIL,
        severity=Severity.HIGH,
        evidence="Task execution role name is missing.",
        recommendation="Provide the ECS task execution role name used for ECR image pulls and awslogs delivery.",
    )
