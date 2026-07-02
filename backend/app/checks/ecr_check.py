from __future__ import annotations

import re

from ..aws.ecr_client import EcrReadonlyClient
from ..core.models import CheckResult, CheckStatus, ReadinessRequest, Severity


ECR_URI_RE = re.compile(
    r"^(?P<account>\d{12})\.dkr\.ecr\.(?P<region>[a-z0-9-]+)\.amazonaws\.com/(?P<repo>[^:@]+)(?::(?P<tag>[^@]+))?(?:@(?P<digest>sha256:[a-f0-9]+))?$"
)


def parse_ecr_image_uri(image: str) -> dict[str, str] | None:
    match = ECR_URI_RE.match(image)
    if not match:
        return None
    data = match.groupdict()
    data["tag"] = data.get("tag") or "latest"
    return {key: value for key, value in data.items() if value}


def run(request: ReadinessRequest) -> CheckResult:
    parsed = parse_ecr_image_uri(request.image)
    if not parsed:
        return CheckResult(
            name="ECR Image Exists",
            status=CheckStatus.FAIL,
            severity=Severity.HIGH,
            evidence="Image URI is not a valid Amazon ECR image URI.",
            recommendation="Use an image URI like 123456789012.dkr.ecr.ap-south-1.amazonaws.com/repository:tag.",
        )

    client = EcrReadonlyClient(region=request.aws_region, profile=request.aws_profile)
    exists, message, metadata = client.image_exists(
        repository_name=parsed["repo"],
        image_tag=parsed.get("tag"),
        image_digest=parsed.get("digest"),
    )
    if exists:
        return CheckResult(
            name="ECR Image Exists",
            status=CheckStatus.PASS,
            severity=Severity.HIGH,
            evidence=message,
            recommendation="Prefer immutable release tags or image digests for production approvals.",
            metadata=metadata,
        )
    return CheckResult(
        name="ECR Image Exists",
        status=CheckStatus.FAIL,
        severity=Severity.HIGH,
        evidence=message,
        recommendation="Push the image to ECR or correct the repository/tag before creating an ECS service.",
    )
