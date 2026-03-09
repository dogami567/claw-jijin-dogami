from fastapi import FastAPI

from .routes.capabilities import router as capabilities_router
from .routes.event import router as event_router
from .routes.fund import router as fund_router
from .routes.health import router as health_router
from .routes.integration import router as integration_router
from .routes.jobs import router as jobs_router
from .routes.portfolio import router as portfolio_router
from .routes.providers import router as providers_router
from .routes.recommendation import router as recommendation_router
from .routes.replay import router as replay_router
from .routes.sync import router as sync_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="claw-jijin-dogami",
        version="0.1.0",
        description="Independent fund analysis service for clawdbot.",
    )
    app.include_router(capabilities_router)
    app.include_router(event_router)
    app.include_router(fund_router)
    app.include_router(health_router)
    app.include_router(integration_router)
    app.include_router(jobs_router)
    app.include_router(portfolio_router)
    app.include_router(providers_router)
    app.include_router(recommendation_router)
    app.include_router(replay_router)
    app.include_router(sync_router)
    return app


app = create_app()
