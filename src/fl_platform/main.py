from contextlib import asynccontextmanager

from fastapi import FastAPI

from fl_platform.api.v1.router import v1_router
from fl_platform.config import Settings
from fl_platform.db.base import Base
from fl_platform.db.engine import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(
        title=settings.app_name,
        description="Film Language Agent Platform — AI agents for film production pipeline",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(v1_router)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
