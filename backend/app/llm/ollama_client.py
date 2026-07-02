from __future__ import annotations

import json
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from ..core.config import get_settings
from .base import SummaryProvider
from .rule_based_summary import RuleBasedSummaryProvider


class OllamaSummaryProvider(SummaryProvider):
    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: float = 10.0) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout

    def summarize(self, payload: dict[str, Any]) -> str:
        prompt = self._build_prompt(payload)
        request = Request(
            f"{self.base_url}/api/generate",
            data=json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body.get("response", "").strip() or RuleBasedSummaryProvider().summarize(payload)

    def _build_prompt(self, payload: dict[str, Any]) -> str:
        checks = payload.get("checks", [])
        compact_checks = [
            {
                "name": check.get("name"),
                "status": check.get("status"),
                "severity": check.get("severity"),
                "evidence": check.get("evidence"),
                "recommendation": check.get("recommendation"),
            }
            for check in checks
        ]
        return (
            "You are a senior DevOps engineer reviewing ECS/Fargate deployment readiness.\n"
            "Produce a concise, evidence-based summary with these headings:\n"
            "Overall deployment readiness, Top risks, Recommended next actions, Interview-style explanation.\n"
            "Do not include secret values. Use the evidence provided.\n\n"
            f"Final status: {payload.get('final_status')}\n"
            f"Score: {payload.get('score')}\n"
            f"Checks: {json.dumps(compact_checks, indent=2)}"
        )


def generate_summary(payload: dict[str, Any]) -> tuple[str, str, str | None]:
    settings = get_settings()
    fallback = RuleBasedSummaryProvider()

    if settings.llm_provider.lower() != "ollama":
        return fallback.summarize(payload), "rule-based", "LLM_PROVIDER is not ollama, generated rule-based summary."

    try:
        summary = OllamaSummaryProvider().summarize(payload)
        return summary, f"ollama:{settings.ollama_model}", None
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        warning = f"Ollama unavailable, generated rule-based summary. Detail: {exc}"
        return fallback.summarize(payload), "rule-based", warning
