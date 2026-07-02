from backend.app.core.models import CheckResult, CheckStatus, Severity
from backend.app.core.scoring import calculate_score, determine_final_status


def check(name: str, status: CheckStatus, severity: Severity) -> CheckResult:
    return CheckResult(
        name=name,
        status=status,
        severity=severity,
        evidence="evidence",
        recommendation="recommendation",
    )


def test_calculate_weighted_score() -> None:
    checks = [
        check("image", CheckStatus.PASS, Severity.HIGH),
        check("port", CheckStatus.WARN, Severity.MEDIUM),
        check("logs", CheckStatus.FAIL, Severity.MEDIUM),
    ]

    summary = calculate_score(checks)

    assert summary.score == 62.5
    assert summary.passed == 1
    assert summary.warnings == 1
    assert summary.failed == 1


def test_final_status_ready_requires_no_high_failures() -> None:
    checks = [
        check("image", CheckStatus.PASS, Severity.HIGH),
        check("env", CheckStatus.FAIL, Severity.HIGH),
        check("logs", CheckStatus.PASS, Severity.MEDIUM),
        check("alb", CheckStatus.PASS, Severity.MEDIUM),
    ]

    summary = calculate_score(checks)

    assert determine_final_status(summary).value == "NOT_READY"
    assert summary.high_severity_failures == ["env"]


def test_final_status_ready_with_warnings() -> None:
    checks = [
        check("image", CheckStatus.PASS, Severity.HIGH),
        check("health", CheckStatus.PASS, Severity.HIGH),
        check("env", CheckStatus.PASS, Severity.HIGH),
        check("port", CheckStatus.WARN, Severity.MEDIUM),
    ]

    summary = calculate_score(checks)

    assert summary.score >= 85
    assert determine_final_status(summary).value == "READY"

