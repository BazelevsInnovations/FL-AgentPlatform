from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fl_platform.db.models import AgentRun, Artifact, ArtifactType, Project, RunStatus


class ProjectContext:
    def __init__(self, db: AsyncSession, project: Project):
        self.db = db
        self.project = project

    async def get_latest_run(self, agent_name: str) -> AgentRun | None:
        stmt = (
            select(AgentRun)
            .where(
                AgentRun.project_id == self.project.id,
                AgentRun.agent_name == agent_name,
                AgentRun.status == RunStatus.COMPLETED,
            )
            .order_by(AgentRun.completed_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_agent_output(self, agent_name: str) -> dict | None:
        run = await self.get_latest_run(agent_name)
        if run is None:
            return None
        return run.output_data

    async def get_artifacts(self, agent_name: str) -> list[Artifact]:
        run = await self.get_latest_run(agent_name)
        if run is None:
            return []
        stmt = select(Artifact).where(Artifact.agent_run_id == run.id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def collect_inputs(self, depends_on: list[str]) -> dict:
        inputs = {}
        inputs["script"] = self.project.script_text

        for dep_name in depends_on:
            output = await self.get_agent_output(dep_name)
            if output:
                inputs[dep_name] = output

            artifacts = await self.get_artifacts(dep_name)
            for art in artifacts:
                key = f"{dep_name}.{art.name}"
                if art.content_text:
                    try:
                        inputs[key] = json.loads(art.content_text)
                    except json.JSONDecodeError:
                        inputs[key] = art.content_text
                elif art.file_path:
                    inputs[key] = f"[file:{art.file_path}]"

        return inputs

    async def create_run(self, agent_name: str, step: int, input_data: dict) -> AgentRun:
        run = AgentRun(
            id=uuid.uuid4(),
            project_id=self.project.id,
            agent_name=agent_name,
            step=step,
            status=RunStatus.RUNNING,
            input_data=input_data,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(run)
        await self.db.flush()
        return run

    async def complete_run(
        self,
        run: AgentRun,
        output_data: dict,
        artifacts: list[dict] | None = None,
    ) -> None:
        run.status = RunStatus.COMPLETED
        run.output_data = output_data
        run.completed_at = datetime.now(timezone.utc)

        if artifacts:
            for art_data in artifacts:
                artifact = Artifact(
                    id=uuid.uuid4(),
                    project_id=self.project.id,
                    agent_run_id=run.id,
                    name=art_data["name"],
                    artifact_type=ArtifactType(art_data.get("type", "json")),
                    content_text=art_data.get("content_text"),
                    file_path=art_data.get("file_path"),
                )
                self.db.add(artifact)

        await self.db.flush()

    async def fail_run(self, run: AgentRun, error: str) -> None:
        run.status = RunStatus.FAILED
        run.error = error
        run.completed_at = datetime.now(timezone.utc)
        await self.db.flush()
