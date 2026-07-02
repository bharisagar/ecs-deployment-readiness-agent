from __future__ import annotations

import subprocess
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

from ..core.config import resolve_project_path
from ..core.models import CheckResult, CheckStatus, Mode, ReadinessRequest, Severity


def _http_probe(url: str, timeout: float = 3.0) -> tuple[bool, str]:
    try:
        request = Request(url, method="GET")
        with urlopen(request, timeout=timeout) as response:
            status = response.getcode()
            if 200 <= status < 400:
                return True, f"Health endpoint returned HTTP {status}."
            return False, f"Health endpoint returned HTTP {status}."
    except URLError as exc:
        return False, f"Health endpoint probe failed: {exc.reason}"
    except Exception as exc:  # pragma: no cover - defensive guard around stdlib networking
        return False, f"Health endpoint probe failed: {exc}"


def _run_container_and_probe(request: ReadinessRequest) -> tuple[bool, str]:
    env_file = resolve_project_path(request.local_env_file) if request.local_env_file else None
    command = [
        "docker",
        "run",
        "-d",
        "--rm",
        "-p",
        f"{request.container_port}:{request.container_port}",
    ]
    if env_file and env_file.exists():
        command.extend(["--env-file", str(env_file)])
    command.append(request.image)

    container_id: str | None = None
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            message = (result.stderr or result.stdout or "docker run failed").strip()
            return False, f"Container did not start for health check: {message}"
        container_id = result.stdout.strip()
        url = f"http://localhost:{request.container_port}{request.health_check_path}"
        for _ in range(10):
            ok, message = _http_probe(url)
            if ok:
                return True, message
            time.sleep(1)
        return False, f"Container started, but {url} did not become healthy within 10 seconds."
    finally:
        if container_id:
            subprocess.run(["docker", "stop", container_id], check=False, capture_output=True, text=True, timeout=15)


def run(request: ReadinessRequest) -> CheckResult:
    if request.mode == Mode.MOCK:
        return CheckResult(
            name="Health Check Works",
            status=CheckStatus.PASS,
            severity=Severity.HIGH,
            evidence=f"Mock health check succeeded for {request.health_check_path}.",
            recommendation="Keep health checks fast, dependency-aware, and safe for repeated ALB probes.",
        )

    if not request.allow_local_container_run:
        return CheckResult(
            name="Health Check Works",
            status=CheckStatus.WARN,
            severity=Severity.HIGH,
            evidence="Local container execution is disabled, so the health endpoint was not probed automatically.",
            recommendation=(
                f"Run the container manually and test http://localhost:{request.container_port}"
                f"{request.health_check_path}, or set allow_local_container_run=true."
            ),
        )

    ok, evidence = _run_container_and_probe(request)
    return CheckResult(
        name="Health Check Works",
        status=CheckStatus.PASS if ok else CheckStatus.FAIL,
        severity=Severity.HIGH,
        evidence=evidence,
        recommendation=(
            "Use this health path in the ECS task definition and ALB target group."
            if ok
            else "Fix the app startup or health route before requesting ECS service approval."
        ),
    )
