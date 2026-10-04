from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import capabilities, health, transform


def create_app() -> FastAPI:
    application = FastAPI(
        title="Stringray API",
        version="0.2.0",
        description=(
            "Phase 1 walking skeleton. The executive summary path is a deterministic "
            "integration stub; AI transformation is not implemented."
        ),
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.include_router(health.router)
    application.include_router(capabilities.router, prefix="/api/v1")
    application.include_router(transform.router, prefix="/api/v1")
    return application


app = create_app()
