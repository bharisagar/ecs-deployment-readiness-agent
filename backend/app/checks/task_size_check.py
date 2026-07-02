from __future__ import annotations

from ..core.models import CheckResult, CheckStatus, ReadinessRequest, Severity


VALID_FARGATE_COMBINATIONS: dict[int, list[int]] = {
    256: [512, 1024, 2048],
    512: [1024, 2048, 3072, 4096],
    1024: list(range(2048, 8192 + 1, 1024)),
    2048: list(range(4096, 16384 + 1, 1024)),
    4096: list(range(8192, 30720 + 1, 1024)),
}


def is_valid_fargate_size(cpu: int, memory: int) -> bool:
    return memory in VALID_FARGATE_COMBINATIONS.get(cpu, [])


def run(request: ReadinessRequest) -> CheckResult:
    if is_valid_fargate_size(request.task_cpu, request.task_memory):
        return CheckResult(
            name="Task CPU/Memory Valid",
            status=CheckStatus.PASS,
            severity=Severity.HIGH,
            evidence=f"{request.task_cpu} CPU units and {request.task_memory} MB memory is a valid Fargate size.",
            recommendation="Keep the task size aligned with load test data and autoscaling targets.",
        )

    valid_memory = VALID_FARGATE_COMBINATIONS.get(request.task_cpu)
    recommendation = (
        f"For {request.task_cpu} CPU units, choose one of: {valid_memory} MB."
        if valid_memory
        else f"Choose a valid Fargate CPU value: {sorted(VALID_FARGATE_COMBINATIONS)}."
    )
    return CheckResult(
        name="Task CPU/Memory Valid",
        status=CheckStatus.FAIL,
        severity=Severity.HIGH,
        evidence=f"{request.task_cpu} CPU units and {request.task_memory} MB memory is not a valid Fargate combination.",
        recommendation=recommendation,
    )
