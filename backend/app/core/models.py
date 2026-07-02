from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Mode(str, Enum):
    LOCAL = "local"
    AWS_READONLY = "aws-readonly"
    MOCK = "mock"


class CheckStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class Severity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"


class FinalStatus(str, Enum):
    READY = "READY"
    READY_WITH_WARNINGS = "READY_WITH_WARNINGS"
    NOT_READY = "NOT_READY"


class ReadinessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image: str = Field(..., min_length=1)
    aws_region: str = "ap-south-1"
    aws_profile: str | None = "default"
    mode: Mode = Mode.MOCK
    container_port: int = Field(default=8080, ge=1, le=65535)
    health_check_path: str = "/health"
    required_env_vars: list[str] = Field(default_factory=list)
    required_dependencies: list[str] = Field(default_factory=list)
    task_cpu: int = 512
    task_memory: int = 1024
    cloudwatch_log_group: str | None = None
    task_execution_role_name: str | None = None
    alb_health_check_path: str = "/health"
    local_env_file: str | None = ".env.sample"
    allow_local_container_run: bool = False
    dependency_connectivity_check: bool = False
    target_group_arn: str | None = None
    project_dir: str = "."
    dockerfile_path: str | None = "Dockerfile"
    selected_config_files: list[str] = Field(default_factory=list)

    @field_validator("health_check_path", "alb_health_check_path")
    @classmethod
    def normalize_path(cls, value: str) -> str:
        value = value.strip() or "/"
        return value if value.startswith("/") else f"/{value}"

    @field_validator("required_env_vars", "required_dependencies", "selected_config_files")
    @classmethod
    def trim_list_values(cls, values: list[str]) -> list[str]:
        return [item.strip() for item in values if item and item.strip()]


class CheckResult(BaseModel):
    name: str
    status: CheckStatus
    severity: Severity
    evidence: str
    recommendation: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScoreSummary(BaseModel):
    score: float
    passed: int
    warnings: int
    failed: int
    total: int
    high_severity_failures: list[str] = Field(default_factory=list)


class ArtifactPaths(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    markdown: str | None = None
    json_path: str | None = Field(default=None, alias="json")


class ReadinessReport(BaseModel):
    report_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    input: ReadinessRequest
    checks: list[CheckResult]
    score_summary: ScoreSummary
    final_status: FinalStatus
    ai_summary: str
    ai_summary_provider: str
    ai_summary_warning: str | None = None
    artifacts: ArtifactPaths = Field(default_factory=ArtifactPaths)

    @property
    def score(self) -> float:
        return self.score_summary.score

