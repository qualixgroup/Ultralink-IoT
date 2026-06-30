from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.infrastructure.cache import get_redis_client
from app.infrastructure.database.seed import ensure_default_admin
from app.infrastructure.database.session import engine
from app.infrastructure.thingsboard.client import thingsboard_client
from app.modules.ai.router import router as ai_router
from app.modules.alerts.router import router as alerts_router
from app.modules.audit.router import router as audit_router
from app.modules.auth.router import router as auth_router
from app.modules.companies.router import router as companies_router
from app.modules.dashboards.router import router as dashboards_router
from app.modules.devices.router import router as devices_router
from app.modules.integrations.router import router as integrations_router
from app.modules.telemetry.router import router as telemetry_router
from app.modules.users.router import router as users_router
from app.modules.workflows.router import router as workflows_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_default_admin()
    yield


app = FastAPI(
    title=settings.app_name,
    description="API privada da plataforma Ultralink IoT. O ThingsBoard atua somente como motor interno de telemetria.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


def _check_database() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return {"status": "error"}
    return {"status": "ok"}


def _check_redis() -> dict[str, str]:
    redis_client = get_redis_client()
    try:
        if not redis_client.ping():
            return {"status": "error"}
    except RedisError:
        return {"status": "error"}
    finally:
        redis_client.close()
    return {"status": "ok"}


async def _check_thingsboard() -> dict[str, str]:
    try:
        await thingsboard_client.health()
    except Exception:
        return {"status": "error"}
    return {"status": "ok"}


@app.get("/health/full", tags=["health"])
async def full_health_check() -> JSONResponse:
    checks = {
        "api": {"status": "ok"},
        "database": _check_database(),
        "redis": _check_redis(),
        "thingsboard": await _check_thingsboard(),
    }
    is_healthy = all(check["status"] == "ok" for check in checks.values())
    payload: dict[str, object] = {
        "status": "ok" if is_healthy else "degraded",
        "service": settings.app_name,
        "checks": checks,
    }
    return JSONResponse(
        status_code=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload,
    )


app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(users_router, prefix=settings.api_v1_prefix)
app.include_router(companies_router, prefix=settings.api_v1_prefix)
app.include_router(devices_router, prefix=settings.api_v1_prefix)
app.include_router(dashboards_router, prefix=settings.api_v1_prefix)
app.include_router(telemetry_router, prefix=settings.api_v1_prefix)
app.include_router(alerts_router, prefix=settings.api_v1_prefix)
app.include_router(audit_router, prefix=settings.api_v1_prefix)
app.include_router(integrations_router, prefix=settings.api_v1_prefix)
app.include_router(ai_router, prefix=settings.api_v1_prefix)
app.include_router(workflows_router, prefix=settings.api_v1_prefix)
