from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any

from ..core.models import CheckResult, CheckStatus, Mode, ReadinessRequest, Severity


def inspect_local_image(image: str) -> tuple[bool, dict[str, Any] | None, str | None]:
    if not shutil.which("docker"):
        return False, None, "Docker CLI is not installed or not on PATH."

    try:
        result = subprocess.run(
            ["docker", "image", "inspect", image],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        return False, None, f"Docker image inspect failed: {exc}"

    if result.returncode != 0:
        message = (result.stderr or result.stdout or "Image not found.").strip()
        return False, None, message

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return False, None, "Docker returned non-JSON image metadata."

    metadata = payload[0] if payload else {}
    return True, metadata, None


def run(request: ReadinessRequest) -> CheckResult:
    if request.mode == Mode.MOCK:
        return CheckResult(
            name="Docker Image Exists",
            status=CheckStatus.PASS,
            severity=Severity.HIGH,
            evidence=f"Mock validation found image {request.image}.",
            recommendation="Pin production deployments to immutable tags or image digests.",
        )

    ok, metadata, error = inspect_local_image(request.image)
    if ok:
        image_id = str(metadata.get("Id", ""))[:19] if metadata else "unknown"
        return CheckResult(
            name="Docker Image Exists",
            status=CheckStatus.PASS,
            severity=Severity.HIGH,
            evidence=f"Local Docker image is available. Image ID prefix: {image_id}.",
            recommendation="Use a versioned tag or digest for production ECS deployments.",
            metadata={"image_id_prefix": image_id},
        )

    return CheckResult(
        name="Docker Image Exists",
        status=CheckStatus.FAIL,
        severity=Severity.HIGH,
        evidence=f"Local Docker image {request.image} was not found. {error}",
        recommendation="Build or pull the image locally, or run aws-readonly mode to validate the image in ECR.",
    )
