from fastapi import APIRouter

from fl_platform.api.v1.agents import router as agents_router
from fl_platform.api.v1.projects import router as projects_router
from fl_platform.api.v1.prompts import router as prompts_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(projects_router)
v1_router.include_router(agents_router)
v1_router.include_router(prompts_router)
