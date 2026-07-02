from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit


SENSITIVE_KEY_RE = re.compile(
    r"(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key)",
    re.IGNORECASE,
)


def mask_value(value: str | None) -> str:
    if not value:
        return ""
    text = str(value)
    if len(text) <= 4:
        return "***"
    return f"{text[:2]}***{text[-2:]}"


def mask_key_value_line(line: str) -> str:
    """Mask the value side of KEY=value style content."""

    if "=" not in line:
        return line
    key, _, value = line.partition("=")
    if not SENSITIVE_KEY_RE.search(key):
        return line
    return f"{key}=***" if value.strip() else f"{key}="


def mask_url(url: str) -> str:
    try:
        parts = urlsplit(url)
    except ValueError:
        return re.sub(r"://([^:@/\s]+):([^@/\s]+)@", r"://***:***@", url)

    if not parts.username and not parts.password:
        return url

    host = parts.hostname or ""
    if parts.port:
        host = f"{host}:{parts.port}"
    safe_netloc = f"***:***@{host}"
    return urlunsplit((parts.scheme, safe_netloc, parts.path, parts.query, parts.fragment))


def redact_text(text: str) -> str:
    text = re.sub(r"://([^:@/\s]+):([^@/\s]+)@", r"://***:***@", text)
    return "\n".join(mask_key_value_line(line) for line in text.splitlines())
