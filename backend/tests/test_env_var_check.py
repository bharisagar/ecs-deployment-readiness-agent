from backend.app.checks.env_var_check import run
from backend.app.core.models import CheckStatus, ReadinessRequest


def test_missing_env_vars_are_reported_without_values(tmp_path) -> None:
    env_file = tmp_path / ".env.sample"
    env_file.write_text("APP_ENV=local\nREDIS_URL=redis://localhost:6379\n", encoding="utf-8")
    request = ReadinessRequest(
        image="sample-app:local",
        mode="local",
        required_env_vars=["DATABASE_URL", "REDIS_URL", "APP_ENV"],
        project_dir=str(tmp_path),
        local_env_file=".env.sample",
    )

    result = run(request)

    assert result.status == CheckStatus.FAIL
    assert result.metadata["present"] == ["REDIS_URL", "APP_ENV"]
    assert result.metadata["missing"] == ["DATABASE_URL"]
    assert "redis://localhost:6379" not in result.evidence
