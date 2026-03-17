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


async def get_artifacts_detail(
    db: AsyncSession,
    project_id: uuid.UUID,
    agent_name: str | None = None,
    artifact_type: str | None = None,
    step: int | None = None,
    department: str | None = None,
) -> list[dict]:
    """Get artifacts enriched with agent run metadata for the gallery."""
    from fl_platform.agents.registry import ALL_AGENTS

    stmt = (
        select(Artifact, AgentRun)
        .join(AgentRun, Artifact.agent_run_id == AgentRun.id)
        .where(Artifact.project_id == project_id)
    )
    if agent_name:
        stmt = stmt.where(AgentRun.agent_name == agent_name)
    if artifact_type:
        stmt = stmt.where(Artifact.artifact_type == artifact_type)
    if step is not None:
        stmt = stmt.where(AgentRun.step == step)

    stmt = stmt.order_by(Artifact.created_at.desc())
    result = await db.execute(stmt)
    rows = result.all()

    # Fetch model_id from prompt_history for each run (batch)
    run_ids = list({row.AgentRun.id for row in rows})
    model_map: dict[uuid.UUID, str | None] = {}
    if run_ids:
        from fl_platform.db.models import PromptHistory

        ph_stmt = (
            select(PromptHistory.agent_run_id, PromptHistory.model_id)
            .where(PromptHistory.agent_run_id.in_(run_ids))
        )
        ph_result = await db.execute(ph_stmt)
        for ph_row in ph_result.all():
            model_map[ph_row.agent_run_id] = ph_row.model_id

    items = []
    for row in rows:
        art: Artifact = row.Artifact
        run: AgentRun = row.AgentRun
        agent_def = ALL_AGENTS.get(run.agent_name)
        display_name = agent_def.display_name if agent_def else run.agent_name
        dept = agent_def.department if agent_def else "unknown"

        if department and dept.lower() != department.lower():
            continue

        items.append(
            {
                "id": str(art.id),
                "name": art.name,
                "artifact_type": art.artifact_type.value if hasattr(art.artifact_type, "value") else str(art.artifact_type),
                "content_text": art.content_text,
                "file_path": art.file_path,
                "created_at": art.created_at.isoformat() if art.created_at else None,
                "agent_name": run.agent_name,
                "agent_display_name": display_name,
                "department": dept,
                "step": run.step,
                "run_status": run.status.value if hasattr(run.status, "value") else str(run.status),
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                "model_id": model_map.get(run.id),
            }
        )

    return items
