from fastapi import FastAPI

from .routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="claw-jijin-dogami",
        version="0.1.0",
        description="Independent fund analysis service for clawdbot.",
    )
    app.include_router(health_router)
    return app


app = create_app()
