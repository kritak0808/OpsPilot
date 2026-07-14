import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.logging import setup_logging
from src.core.exceptions import register_exception_handlers
from src.database.connection import verify_db_health, verify_redis_health
from src.observability.telemetry import initialize_telemetry
from src.routers import auth, users, organizations, teams, projects, repositories, environments, pipelines, kubernetes, observability, ai, governance

def create_app() -> FastAPI:
    # Initialize logger
    setup_logging()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Middleware: CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware: Request trace_id injection
    @app.middleware("http")
    async def inject_trace_id(request: Request, call_next):
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        request.state.trace_id = trace_id
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response

    # Exception Handling
    register_exception_handlers(app)

    # Telemetry
    initialize_telemetry(app)

    # Include Routers
    app.include_router(auth)
    app.include_router(users)
    app.include_router(organizations)
    app.include_router(teams)
    app.include_router(projects)
    app.include_router(repositories)
    app.include_router(environments)
    app.include_router(pipelines)
    app.include_router(kubernetes)
    app.include_router(observability)
    app.include_router(ai)
    app.include_router(governance)

    # System endpoints
    @app.get("/health", tags=["System"])
    async def health_check():
        db_ok = await verify_db_health()
        redis_ok = await verify_redis_health()
        
        status = "healthy" if db_ok and redis_ok else "unhealthy"
        status_code = 200 if status == "healthy" else 503
        
        return {
            "status": status,
            "components": {
                "postgresql": "up" if db_ok else "down",
                "redis": "up" if redis_ok else "down"
            }
        }

    @app.get("/api/v1/version", tags=["System"])
    async def version_endpoint():
        return {
            "service": settings.PROJECT_NAME,
            "version": "1.0.0",
            "api_version": settings.API_VERSION,
            "environment": settings.ENV
        }

    return app

app = create_app()
