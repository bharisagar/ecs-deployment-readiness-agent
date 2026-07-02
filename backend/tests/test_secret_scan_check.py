from backend.app.checks.secret_scan_check import run
from backend.app.core.models import CheckStatus, ReadinessRequest


def test_secret_scan_masks_values(tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "AWS_SECRET_ACCESS_KEY=supersecretvalue\npassword=mydbpassword\nAPP_ENV=local\n",
        encoding="utf-8",
    )
    request = ReadinessRequest(
        image="sample-app:local",
        mode="local",
        project_dir=str(tmp_path),
        local_env_file=".env",
    )

    result = run(request)

    assert result.status == CheckStatus.FAIL
    assert "supersecretvalue" not in result.evidence
    assert "mydbpassword" not in result.evidence
    assert "AWS_SECRET_ACCESS_KEY=***" in result.evidence
    assert "password=***" in result.evidence


def test_secret_scan_ignores_blank_secret_keys(tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("AWS_SECRET_ACCESS_KEY=\npassword=\n", encoding="utf-8")
    request = ReadinessRequest(
        image="sample-app:local",
        mode="local",
        project_dir=str(tmp_path),
        local_env_file=".env",
    )

    result = run(request)

    assert result.status == CheckStatus.PASS
