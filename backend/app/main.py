from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analyze, capabilities, health, transform


def create_app(analysis_provider=None) -> FastAPI:
    application = FastAPI(
        title="Stringray API",
        version="0.2.0",
        description=(
            "Phase 1 walking skeleton plus Phase 2B provider-backed source analysis. "
            "The executive summary path is a deterministic integration stub; "
            "/api/v1/analyze performs structured analysis only when configured."
        ),
    )
    application.state.analysis_provider = analysis_provider
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.include_router(health.router)
    application.include_router(capabilities.router, prefix="/api/v1")
    application.include_router(transform.router, prefix="/api/v1")
    application.include_router(analyze.router, prefix="/api/v1")
    analyze.register_analysis_error_handlers(application)
    return application


app = create_app()
