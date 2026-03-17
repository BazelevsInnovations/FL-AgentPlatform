from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from fl_platform.config import Settings
from fl_platform.db.engine import get_db_session
from fl_platform.dependencies import get_settings
from fl_platform.schemas.project import ProjectCreate, ProjectDetail, ProjectResponse
from fl_platform.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreate,
    db: AsyncSession = Depends(get_db_session),
):
    project = await project_service.create_project(db, body.name, body.script_text)
    return project


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db_session)):
    return await project_service.list_projects(db)


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    project = await project_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    return project


@router.put("/{project_id}/script", response_model=ProjectResponse)
async def update_script(
    project_id: uuid.UUID,
    body: ProjectCreate,
    db: AsyncSession = Depends(get_db_session),
):
    project = await project_service.update_project_script(db, project_id, body.script_text)
    if project is None:
        raise HTTPException(404, "Project not found")
    return project
