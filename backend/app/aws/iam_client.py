from __future__ import annotations

from .session import create_client


class IamReadonlyClient:
    def __init__(self, region: str, profile: str | None) -> None:
        self.region = region
        self.profile = profile

    def execution_role_status(self, role_name: str) -> tuple[bool, list[str], str]:
        client_result = create_client("iam", self.region, self.profile)
        if not client_result.ok:
            return False, [], client_result.error or "Unable to create IAM client."

        try:
            client_result.client.get_role(RoleName=role_name)
            response = client_result.client.list_attached_role_policies(RoleName=role_name)
        except Exception as exc:
            return False, [], f"IAM role lookup failed for {role_name}: {exc}"

        policies = [
            item.get("PolicyName", "")
            for item in response.get("AttachedPolicies", [])
            if item.get("PolicyName")
        ]
        if policies:
            return True, policies, f"IAM role {role_name} exists with attached policies: {policies}."
        return True, [], f"IAM role {role_name} exists, but no attached managed policies were found."
