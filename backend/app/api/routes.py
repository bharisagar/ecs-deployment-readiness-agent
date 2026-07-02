from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..core.config import get_settings
from ..core.models import ReadinessRequest
from ..core.runner import run_readiness_check
from ..storage.local_store import LocalReportStore


router = APIRouter()
store = LocalReportStore()


@router.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}


@router.post("/readiness/check")
def create_readiness_check(request: ReadinessRequest):
    report = run_readiness_check(request)
    return store.save(report)


@router.get("/readiness/report/{report_id}")
def get_readiness_report(report_id: str):
    report = store.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/readiness/history")
def readiness_history():
    return {"reports": store.list_reports()}


@router.get("/config/sample")
def sample_config():
    return {
        "image": "516569236000.dkr.ecr.ap-south-1.amazonaws.com/sample-app:latest",
        "aws_region": "ap-south-1",
        "aws_profile": "default",
        "mode": "mock",
        "container_port": 8080,
        "health_check_path": "/health",
        "required_env_vars": ["DATABASE_URL", "REDIS_URL", "APP_ENV"],
        "required_dependencies": ["postgres", "redis"],
        "task_cpu": 512,
        "task_memory": 1024,
        "cloudwatch_log_group": "/ecs/sample-app",
        "task_execution_role_name": "ecsTaskExecutionRole",
        "alb_health_check_path": "/health",
        "local_env_file": ".env.sample",
        "allow_local_container_run": False,
        "dependency_connectivity_check": False,
    }
