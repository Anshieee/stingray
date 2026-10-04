from fastapi import FastAPI

from app.api.routes import capabilities, health


def create_app() -> FastAPI:
    application = FastAPI(
        title="Stringray API",
        version="0.1.0",
        description="Phase 0 foundation. AI transformation is not implemented.",
    )
    application.include_router(health.router)
    application.include_router(capabilities.router, prefix="/api/v1")
    return application


app = create_app()
