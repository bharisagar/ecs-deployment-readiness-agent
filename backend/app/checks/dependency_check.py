from __future__ import annotations

import socket
from urllib.parse import urlsplit

from ..core.config import PROJECT_ROOT, resolve_project_path
from ..core.models import CheckResult, CheckStatus, Mode, ReadinessRequest, Severity
from ..core.redaction import mask_url
from .env_var_check import parse_env_file


DEPENDENCY_ENV_HINTS = {
    "postgres": ["DATABASE_URL", "POSTGRES_URL", "PGHOST"],
    "postgresql": ["DATABASE_URL", "POSTGRES_URL", "PGHOST"],
    "redis": ["REDIS_URL", "REDIS_HOST"],
}


def _try_connect(url: str, timeout: float = 2.0) -> tuple[bool, str]:
    parsed = urlsplit(url)
    if not parsed.hostname:
        return False, "No hostname found in dependency URL."
    port = parsed.port or (5432 if parsed.scheme.startswith("postgres") else 6379)
    try:
        with socket.create_connection((parsed.hostname, port), timeout=timeout):
            return True, f"Connectivity succeeded for {parsed.hostname}:{port}."
    except OSError as exc:
        return False, f"Connectivity failed for {parsed.hostname}:{port}: {exc}"


def run(request: ReadinessRequest) -> CheckResult:
    if request.mode == Mode.MOCK:
        return CheckResult(
            name="Dependencies Documented",
            status=CheckStatus.PASS,
            severity=Severity.MEDIUM,
            evidence=f"Mock configuration documents dependencies: {request.required_dependencies or ['postgres', 'redis']}.",
            recommendation="Keep connection endpoints out of reports and store credentials in Secrets Manager or SSM.",
        )

    project_dir = resolve_project_path(request.project_dir) or PROJECT_ROOT
    env_file = resolve_project_path(request.local_env_file, project_dir) if request.local_env_file else None
    env_values = parse_env_file(env_file) if env_file else {}

    missing: list[str] = []
    documented: list[str] = []
    connectivity_notes: list[str] = []
    for dependency in request.required_dependencies:
        key = dependency.lower()
        hints = DEPENDENCY_ENV_HINTS.get(key, [])
        has_hint = any(var in request.required_env_vars or var in env_values for var in hints)
        if has_hint:
            documented.append(dependency)
        else:
            missing.append(dependency)

        if request.dependency_connectivity_check:
            for var in hints:
                value = env_values.get(var)
                if value and "://" in value:
                    ok, note = _try_connect(value)
                    connectivity_notes.append(f"{var}: {note} URL={mask_url(value)}")
                    if not ok and dependency not in missing:
                        missing.append(dependency)
                    break

    status = CheckStatus.PASS if not missing else CheckStatus.WARN
    evidence = f"Documented dependencies: {documented or 'none'}. Missing documentation: {missing or 'none'}."
    if connectivity_notes:
        evidence += " Connectivity: " + " ".join(connectivity_notes)

    return CheckResult(
        name="Dependencies Documented",
        status=status,
        severity=Severity.MEDIUM,
        evidence=evidence,
        recommendation="Document service dependencies and confirm network paths before ECS service creation.",
        metadata={"documented": documented, "missing": missing},
    )
