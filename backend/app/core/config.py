from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORTS_DIR = PROJECT_ROOT / "reports"
DEFAULT_PROJECT_DIR = PROJECT_ROOT


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables or .env files."""

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env.example", PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ECS Deployment Readiness Agent"
    app_version: str = "0.1.0"
    default_mode: Literal["mock", "local", "aws-readonly"] = "mock"
    llm_provider: str = Field(default="ollama", alias="LLM_PROVIDER")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.1", alias="OLLAMA_MODEL")
    request_timeout_seconds: float = 5.0


@lru_cache
def get_settings() -> Settings:
    return Settings()


def resolve_project_path(path_value: str | None, base_dir: Path | None = None) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path.resolve()
    base = base_dir or PROJECT_ROOT
    return (base / path).resolve()
