from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fl_platform.db.models import Project, ProjectStatus


async def create_project(db: AsyncSession, name: str, script_text: str = "") -> Project:
    project = Project(
        id=uuid.uuid4(),
        name=name,
        script_text=script_text,
        status=ProjectStatus.DRAFT,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def get_project(db: AsyncSession, project_id: uuid.UUID) -> Project | None:
    return await db.get(Project, project_id)


async def list_projects(db: AsyncSession) -> list[Project]:
    stmt = select(Project).order_by(Project.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_project_script(
    db: AsyncSession, project_id: uuid.UUID, script_text: str
) -> Project | None:
    project = await db.get(Project, project_id)
    if project is None:
        return None
    project.script_text = script_text
    await db.commit()
    await db.refresh(project)
    return project
