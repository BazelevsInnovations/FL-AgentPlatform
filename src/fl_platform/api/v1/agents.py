from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from fl_platform.agents.registry import ALL_AGENTS, list_agents
from fl_platform.config import Settings
from fl_platform.db.engine import get_db_session
from fl_platform.dependencies import get_settings
from fl_platform.pipeline.dag import PipelineDAG
from fl_platform.agents.registry import list_departments
from fl_platform.schemas.agent import (
    AgentInfo,
    ArtifactDetailResponse,
    AgentRunRequest,
    AgentRunResponse,
    ArtifactResponse,
    PipelineStepRequest,
    PromptHistoryResponse,
)
from fl_platform.db.models import PromptHistory
from fl_platform.services import agent_service, project_service

router = APIRouter(tags=["agents"])


@router.get("/agents", response_model=list[AgentInfo])
async def get_agents():
    return [
        AgentInfo(
            name=a.name,
            display_name=a.display_name,
            department=a.department,
            step=a.step,
            executor_type=a.executor_type,
            input_description=a.input_description,
            output_description=a.output_description,
            depends_on=a.depends_on,
        )
        for a in list_agents()
    ]


@router.get("/pipeline/dag")
async def get_pipeline_dag():
    dag = PipelineDAG(ALL_AGENTS)
    return dag.to_dict()


@router.post("/projects/{project_id}/agents/{agent_name}/run")
async def run_agent(
    project_id: uuid.UUID,
    agent_name: str,
    body: AgentRunRequest | None = None,
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
):
    project = await project_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    try:
        result = await agent_service.run_agent(db, project, agent_name, settings)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/projects/{project_id}/agents/{agent_name}/runs", response_model=list[AgentRunResponse])
async def get_agent_runs(
    project_id: uuid.UUID,
    agent_name: str,
    db: AsyncSession = Depends(get_db_session),
):
    runs = await agent_service.get_agent_runs(db, project_id, agent_name)
    return runs


@router.post("/projects/{project_id}/pipeline/run-step")
async def run_pipeline_step(
    project_id: uuid.UUID,
    body: PipelineStepRequest,
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
):
    project = await project_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    results = await agent_service.run_step(db, project, body.step, settings)
    return results


@router.post("/projects/{project_id}/pipeline/run-all")
async def run_pipeline_all(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
):
    project = await project_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    results = await agent_service.run_all(db, project, settings)
    return results


@router.get("/projects/{project_id}/gallery")
async def get_gallery(
    project_id: uuid.UUID,
    agent_name: str | None = None,
    artifact_type: str | None = None,
    step: int | None = None,
    department: str | None = None,
    db: AsyncSession = Depends(get_db_session),
):
    """Gallery endpoint: artifacts enriched with agent/run metadata."""
    items = await agent_service.get_artifacts_detail(
        db, project_id,
        agent_name=agent_name,
        artifact_type=artifact_type,
        step=step,
        department=department,
    )
    return items


@router.get("/projects/{project_id}/gallery/filters")
async def get_gallery_filters(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Return available filter values for the gallery."""
    all_items = await agent_service.get_artifacts_detail(db, project_id)
    agent_names = sorted({item["agent_name"] for item in all_items})
    types = sorted({item["artifact_type"] for item in all_items})
    steps = sorted({item["step"] for item in all_items})
    departments = sorted({item["department"] for item in all_items})
    return {
        "agent_names": agent_names,
        "artifact_types": types,
        "steps": steps,
        "departments": departments,
    }


@router.get("/projects/{project_id}/artifacts", response_model=list[ArtifactResponse])
async def get_artifacts(
    project_id: uuid.UUID,
    agent_name: str | None = None,
    db: AsyncSession = Depends(get_db_session),
):
    artifacts = await agent_service.get_artifacts(db, project_id, agent_name)
    return artifacts


@router.get("/projects/{project_id}/artifacts/{artifact_id}/download")
async def download_artifact(
    project_id: uuid.UUID,
    artifact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    artifact = await agent_service.get_artifact(db, artifact_id)
    if artifact is None or str(artifact.project_id) != str(project_id):
        raise HTTPException(404, "Artifact not found")
    if artifact.file_path:
        return FileResponse(artifact.file_path)
    if artifact.content_text:
        return {"content": artifact.content_text}
    raise HTTPException(404, "No content available")


@router.get(
    "/projects/{project_id}/agents/{agent_name}/prompt-history",
    response_model=list[PromptHistoryResponse],
)
async def get_prompt_history(
    project_id: uuid.UUID,
    agent_name: str,
    db: AsyncSession = Depends(get_db_session),
):
    from sqlalchemy import select

    stmt = (
        select(PromptHistory)
        .where(
            PromptHistory.project_id == project_id,
            PromptHistory.agent_name == agent_name,
        )
        .order_by(PromptHistory.created_at.desc())
        .limit(20)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
