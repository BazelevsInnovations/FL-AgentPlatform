from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fl_platform.db.models import AgentRun, Artifact, Project
from fl_platform.config import Settings
from fl_platform.pipeline.runner import PipelineRunner


async def run_agent(
    db: AsyncSession, project: Project, agent_name: str, settings: Settings
) -> dict:
    runner = PipelineRunner(db, settings)
    return await runner.run_agent(project, agent_name)


async def run_step(
    db: AsyncSession, project: Project, step: int, settings: Settings
) -> list[dict]:
    runner = PipelineRunner(db, settings)
    return await runner.run_step(project, step)


async def run_all(
    db: AsyncSession, project: Project, settings: Settings
) -> list[dict]:
    runner = PipelineRunner(db, settings)
    return await runner.run_all(project)


async def get_agent_runs(
    db: AsyncSession, project_id: uuid.UUID, agent_name: str | None = None
) -> list[AgentRun]:
    stmt = select(AgentRun).where(AgentRun.project_id == project_id)
    if agent_name:
        stmt = stmt.where(AgentRun.agent_name == agent_name)
    stmt = stmt.order_by(AgentRun.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_artifacts(
    db: AsyncSession, project_id: uuid.UUID, agent_name: str | None = None
) -> list[Artifact]:
    stmt = select(Artifact).where(Artifact.project_id == project_id)
    if agent_name:
        stmt = stmt.join(AgentRun).where(AgentRun.agent_name == agent_name)
    stmt = stmt.order_by(Artifact.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_artifact(db: AsyncSession, artifact_id: uuid.UUID) -> Artifact | None:
    return await db.get(Artifact, artifact_id)
