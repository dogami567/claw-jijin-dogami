from fastapi import FastAPI

from .routes.event import router as event_router
from .routes.health import router as health_router
from .routes.jobs import router as jobs_router
from .routes.portfolio import router as portfolio_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="claw-jijin-dogami",
        version="0.1.0",
        description="Independent fund analysis service for clawdbot.",
    )
    app.include_router(event_router)
    app.include_router(health_router)
    app.include_router(jobs_router)
    app.include_router(portfolio_router)
    return app


app = create_app()
