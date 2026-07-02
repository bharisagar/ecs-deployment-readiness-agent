from __future__ import annotations

from .session import create_client


class CloudWatchReadonlyClient:
    def __init__(self, region: str, profile: str | None) -> None:
        self.region = region
        self.profile = profile

    def log_group_exists(self, log_group_name: str) -> tuple[bool, str]:
        client_result = create_client("logs", self.region, self.profile)
        if not client_result.ok:
            return False, client_result.error or "Unable to create CloudWatch Logs client."

        try:
            response = client_result.client.describe_log_groups(
                logGroupNamePrefix=log_group_name,
                limit=50,
            )
        except Exception as exc:
            return False, f"CloudWatch log group lookup failed: {exc}"

        for group in response.get("logGroups", []):
            if group.get("logGroupName") == log_group_name:
                return True, f"CloudWatch log group exists: {log_group_name}."
        return False, f"CloudWatch log group was not found: {log_group_name}."
