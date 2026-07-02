from __future__ import annotations

from .session import create_client


class Elbv2ReadonlyClient:
    def __init__(self, region: str, profile: str | None) -> None:
        self.region = region
        self.profile = profile

    def target_group_health_path(self, target_group_arn: str) -> tuple[bool, str | None, str]:
        client_result = create_client("elbv2", self.region, self.profile)
        if not client_result.ok:
            return False, None, client_result.error or "Unable to create ELBv2 client."

        try:
            response = client_result.client.describe_target_groups(TargetGroupArns=[target_group_arn])
        except Exception as exc:
            return False, None, f"Target group lookup failed: {exc}"

        target_groups = response.get("TargetGroups", [])
        if not target_groups:
            return False, None, f"Target group was not found: {target_group_arn}."
        path = target_groups[0].get("HealthCheckPath")
        return True, path, f"Target group health check path is {path}."
