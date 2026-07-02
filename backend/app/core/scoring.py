from __future__ import annotations

from .models import CheckResult, CheckStatus, FinalStatus, ScoreSummary, Severity


SEVERITY_WEIGHTS: dict[Severity, int] = {
    Severity.HIGH: 10,
    Severity.MEDIUM: 5,
}

STATUS_MULTIPLIERS: dict[CheckStatus, float] = {
    CheckStatus.PASS: 1.0,
    CheckStatus.WARN: 0.5,
    CheckStatus.FAIL: 0.0,
}


def calculate_score(checks: list[CheckResult]) -> ScoreSummary:
    total_weight = sum(SEVERITY_WEIGHTS[check.severity] for check in checks)
    earned = sum(
        SEVERITY_WEIGHTS[check.severity] * STATUS_MULTIPLIERS[check.status]
        for check in checks
    )
    score = round((earned / total_weight) * 100, 2) if total_weight else 0.0
    high_failures = [
        check.name
        for check in checks
        if check.severity == Severity.HIGH and check.status == CheckStatus.FAIL
    ]
    return ScoreSummary(
        score=score,
        passed=sum(1 for check in checks if check.status == CheckStatus.PASS),
        warnings=sum(1 for check in checks if check.status == CheckStatus.WARN),
        failed=sum(1 for check in checks if check.status == CheckStatus.FAIL),
        total=len(checks),
        high_severity_failures=high_failures,
    )


def determine_final_status(score_summary: ScoreSummary) -> FinalStatus:
    if score_summary.high_severity_failures or score_summary.score < 70:
        return FinalStatus.NOT_READY
    if score_summary.score >= 85:
        return FinalStatus.READY
    return FinalStatus.READY_WITH_WARNINGS
