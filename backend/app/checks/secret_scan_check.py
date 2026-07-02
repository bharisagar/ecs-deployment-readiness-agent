from __future__ import annotations

import re
from pathlib import Path

from ..core.config import PROJECT_ROOT, resolve_project_path
from ..core.models import CheckResult, CheckStatus, Mode, ReadinessRequest, Severity
from ..core.redaction import mask_key_value_line


SECRET_PATTERNS = [
    re.compile(r"\bAWS_ACCESS_KEY_ID\b\s*=\s*(?P<value>\S+)", re.IGNORECASE),
    re.compile(r"\bAWS_SECRET_ACCESS_KEY\b\s*=\s*(?P<value>\S+)", re.IGNORECASE),
    re.compile(r"\bpassword\s*=\s*(?P<value>\S+)", re.IGNORECASE),
    re.compile(r"\bapi_key\s*=\s*(?P<value>\S+)", re.IGNORECASE),
    re.compile(r"\bsecret\s*=\s*(?P<value>\S+)", re.IGNORECASE),
    re.compile(r"\btoken\s*=\s*(?P<value>\S+)", re.IGNORECASE),
    re.compile(r"\bprivate_key\b\s*=\s*(?P<value>\S+)", re.IGNORECASE),
]

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "reports", "__pycache__", ".pytest_cache", "dist", "build"}
CONFIG_EXTENSIONS = {".env", ".yml", ".yaml", ".json", ".toml", ".ini", ".conf", ".cfg"}


def _is_blank_or_placeholder(value: str) -> bool:
    normalized = value.strip().strip('"').strip("'").strip()
    if not normalized:
        return True
    return normalized.lower() in {"changeme", "change-me", "example", "placeholder", "<secret>", "***"}


def _candidate_files(project_dir: Path, request: ReadinessRequest) -> list[Path]:
    explicit: set[Path] = set()
    if request.local_env_file:
        explicit_path = resolve_project_path(request.local_env_file, project_dir)
        if explicit_path:
            explicit.add(explicit_path)
    if request.dockerfile_path:
        dockerfile = resolve_project_path(request.dockerfile_path, project_dir)
        if dockerfile:
            explicit.add(dockerfile)
    for file_name in request.selected_config_files:
        path = resolve_project_path(file_name, project_dir)
        if path:
            explicit.add(path)

    discovered: list[Path] = []
    for path in project_dir.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.name == "Dockerfile" or path.name.startswith(".env") or path.suffix.lower() in CONFIG_EXTENSIONS:
            discovered.append(path)
    return sorted({*explicit, *discovered})


def scan_file(path: Path) -> list[str]:
    findings: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return findings

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for pattern in SECRET_PATTERNS:
            match = pattern.search(stripped)
            if not match:
                continue
            value = match.groupdict().get("value", "")
            if _is_blank_or_placeholder(value):
                continue
            findings.append(f"{path.name}:{line_number}: {mask_key_value_line(stripped)}")
            break
    return findings


def run(request: ReadinessRequest) -> CheckResult:
    if request.mode == Mode.MOCK:
        return CheckResult(
            name="Secrets Not Hardcoded",
            status=CheckStatus.PASS,
            severity=Severity.HIGH,
            evidence="Mock scan found no hardcoded secrets in Dockerfile or selected config files.",
            recommendation="Keep scanning limited to project files and use secret references for ECS tasks.",
        )

    project_dir = resolve_project_path(request.project_dir) or PROJECT_ROOT
    if not project_dir.exists() or not project_dir.is_dir():
        return CheckResult(
            name="Secrets Not Hardcoded",
            status=CheckStatus.FAIL,
            severity=Severity.HIGH,
            evidence=f"Project directory {project_dir} does not exist.",
            recommendation="Provide a valid project_dir so the scanner can inspect Dockerfile, env, and config files.",
        )

    findings: list[str] = []
    for path in _candidate_files(project_dir, request):
        try:
            path.relative_to(project_dir)
        except ValueError:
            continue
        findings.extend(scan_file(path))

    if findings:
        return CheckResult(
            name="Secrets Not Hardcoded",
            status=CheckStatus.FAIL,
            severity=Severity.HIGH,
            evidence=f"Potential hardcoded secrets found: {findings}. Values are masked.",
            recommendation="Remove hardcoded secrets and reference AWS Secrets Manager or SSM Parameter Store from ECS.",
            metadata={"findings": findings},
        )

    return CheckResult(
        name="Secrets Not Hardcoded",
        status=CheckStatus.PASS,
        severity=Severity.HIGH,
        evidence="No hardcoded secret patterns were found in Dockerfile, env files, or selected config files.",
        recommendation="Continue to keep real secrets out of source control and generated reports.",
    )
