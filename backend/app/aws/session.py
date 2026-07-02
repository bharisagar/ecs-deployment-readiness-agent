from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AwsClientResult:
    ok: bool
    client: Any | None = None
    error: str | None = None


def create_client(service_name: str, region: str, profile: str | None) -> AwsClientResult:
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ProfileNotFound
    except ImportError:
        return AwsClientResult(ok=False, error="boto3 is not installed. Install requirements.txt for aws-readonly mode.")

    try:
        session_kwargs: dict[str, str] = {"region_name": region}
        if profile:
            session_kwargs["profile_name"] = profile
        session = boto3.Session(**session_kwargs)
        return AwsClientResult(ok=True, client=session.client(service_name))
    except ProfileNotFound as exc:
        return AwsClientResult(ok=False, error=f"AWS profile not found: {exc}")
    except BotoCoreError as exc:
        return AwsClientResult(ok=False, error=f"Could not create AWS {service_name} client: {exc}")
