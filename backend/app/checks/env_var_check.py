from __future__ import annotations

from pathlib import Path

from ..core.config import PROJECT_ROOT, resolve_project_path
from ..core.models import CheckResult, CheckStatus, Mode, ReadinessRequest, Severity


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def run(request: ReadinessRequest) -> CheckResult:
    if request.mode == Mode.MOCK:
        missing = ["DATABASE_URL"] if "DATABASE_URL" in request.required_env_vars else []
        present = [name for name in request.required_env_vars if name not in missing]
        return CheckResult(
            name="Required Env Vars Present",
            status=CheckStatus.FAIL if missing else CheckStatus.PASS,
            severity=Severity.HIGH,
            evidence=f"Present variables: {present or 'none'}. Missing variables: {missing or 'none'}.",
            recommendation="Add missing variables through ECS task definition environment or Secrets Manager references.",
            metadata={"present": present, "missing": missing},
        )

    project_dir = resolve_project_path(request.project_dir) or PROJECT_ROOT
    env_file = resolve_project_path(request.local_env_file, project_dir) if request.local_env_file else None
    if not env_file or not env_file.exists():
        return CheckResult(
            name="Required Env Vars Present",
            status=CheckStatus.FAIL,
            severity=Severity.HIGH,
            evidence=f"Environment file {request.local_env_file or '<not provided>'} was not found.",
            recommendation="Provide a .env.sample or equivalent non-secret config file listing required variables.",
            metadata={"present": [], "missing": request.required_env_vars},
        )

    values = parse_env_file(env_file)
    present = [name for name in request.required_env_vars if name in values]
    missing = [name for name in request.required_env_vars if name not in values]
    status = CheckStatus.PASS if not missing else CheckStatus.FAIL
    return CheckResult(
        name="Required Env Vars Present",
        status=status,
        severity=Severity.HIGH,
        evidence=f"Present variables: {present or 'none'}. Missing variables: {missing or 'none'}. Values are not reported.",
        recommendation=(
            "Map all required variables in the ECS task definition and put sensitive values in Secrets Manager or SSM."
            if missing
            else "Keep this file as documentation only; do not commit real secret values."
        ),
        metadata={"present": present, "missing": missing, "env_file": str(env_file)},
    )
