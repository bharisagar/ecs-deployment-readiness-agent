from __future__ import annotations

from ..core.models import CheckResult, CheckStatus, Mode, ReadinessRequest, Severity
from .docker_image_check import inspect_local_image


def _extract_exposed_ports(metadata: dict) -> list[str]:
    exposed = metadata.get("Config", {}).get("ExposedPorts") or {}
    return sorted(exposed.keys())


def run(request: ReadinessRequest) -> CheckResult:
    expected = f"{request.container_port}/tcp"

    if request.mode == Mode.MOCK:
        return CheckResult(
            name="Container Port Exposed",
            status=CheckStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=f"Mock image metadata did not declare {expected}.",
            recommendation="Add EXPOSE to the Dockerfile or document the container port in the ECS task definition.",
            metadata={"expected_port": expected, "exposed_ports": []},
        )


    if request.mode == Mode.AWS_READONLY:
        return CheckResult(
            name="Container Port Exposed",
            status=CheckStatus.WARN,
            severity=Severity.MEDIUM,
            evidence="AWS read-only mode does not pull or inspect image layers for EXPOSE metadata.",
            recommendation="Confirm containerPort in the ECS task definition matches the application listener port.",
            metadata={"expected_port": expected, "exposed_ports": []},
        )

    ok, metadata, error = inspect_local_image(request.image)
    if not ok:
        return CheckResult(
            name="Container Port Exposed",
            status=CheckStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=f"Could not inspect local image metadata for exposed ports. {error}",
            recommendation="Confirm the ECS container port maps to the port your application listens on.",
        )

    exposed_ports = _extract_exposed_ports(metadata or {})
    if expected in exposed_ports:
        return CheckResult(
            name="Container Port Exposed",
            status=CheckStatus.PASS,
            severity=Severity.MEDIUM,
            evidence=f"Image metadata exposes {expected}.",
            recommendation="Keep the ECS container port aligned with the image and ALB target group.",
            metadata={"expected_port": expected, "exposed_ports": exposed_ports},
        )

    return CheckResult(
        name="Container Port Exposed",
        status=CheckStatus.WARN,
        severity=Severity.MEDIUM,
        evidence=f"Expected {expected}; image metadata exposes {exposed_ports or 'no ports'}.",
        recommendation="This is not always fatal, but add EXPOSE or document the port clearly for ECS reviewers.",
        metadata={"expected_port": expected, "exposed_ports": exposed_ports},
    )

