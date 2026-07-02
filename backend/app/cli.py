from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from .core.models import ReadinessRequest
from .core.runner import run_readiness_check
from .storage.local_store import LocalReportStore


def _load_config(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(raw)
    return yaml.safe_load(raw)


def check_command(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    payload = _load_config(config_path)
    request = ReadinessRequest.model_validate(payload)
    report = LocalReportStore().save(run_readiness_check(request))
    print("ECS Deployment Readiness Check")
    print(f"Overall status: {report.final_status.value}")
    print(f"Score: {report.score_summary.score}%")
    print(f"Passed count: {report.score_summary.passed}")
    print(f"Warning count: {report.score_summary.warnings}")
    print(f"Failed count: {report.score_summary.failed}")
    print(f"Markdown report path: {report.artifacts.markdown}")
    print(f"JSON report path: {report.artifacts.json_path}")
    if report.ai_summary_warning:
        print(f"Summary warning: {report.ai_summary_warning}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ECS deployment readiness agent")
    subcommands = parser.add_subparsers(dest="command", required=True)
    check = subcommands.add_parser("check", help="Run a readiness check from a JSON or YAML config")
    check.add_argument("--config", required=True, help="Path to readiness config file")
    check.set_defaults(func=check_command)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

