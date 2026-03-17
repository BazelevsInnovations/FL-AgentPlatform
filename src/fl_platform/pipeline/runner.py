from __future__ import annotations

import asyncio
import json
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from fl_platform.agents.base import AgentDefinition
from fl_platform.agents.registry import ALL_AGENTS, get_agent
from fl_platform.db.models import AgentConfig, Project, PromptHistory
from fl_platform.executors.base import BaseExecutor, ExecutorResult
from fl_platform.executors.fal_image import FalImageExecutor
from fl_platform.executors.fal_video import FalVideoExecutor
from fl_platform.executors.llm import LLMExecutor, StubLLMExecutor
from fl_platform.executors.python_script import PythonScriptExecutor
from fl_platform.pipeline.context import ProjectContext
from fl_platform.pipeline.dag import PipelineDAG
from fl_platform.config import Settings

from sqlalchemy import select

logger = logging.getLogger(__name__)


class PipelineRunner:
    def __init__(self, db: AsyncSession, settings: Settings):
        self.db = db
        self.settings = settings
        self.dag = PipelineDAG(ALL_AGENTS)

    def _get_executor(self, agent: AgentDefinition, config: AgentConfig | None) -> BaseExecutor:
        executor_type = agent.executor_type

        if executor_type == "llm":
            provider = self.settings.default_llm_provider
            if provider == "stub":
                return StubLLMExecutor()
            api_key = (
                self.settings.anthropic_api_key
                if provider == "claude"
                else self.settings.openai_api_key
            )
            return LLMExecutor(
                provider=provider,
                api_key=api_key,
                default_model=self.settings.default_llm_model,
            )
        elif executor_type == "fal_image":
            return FalImageExecutor(
                api_key=self.settings.fal_api_key,
                artifacts_dir=self.settings.artifacts_dir,
                default_model=self.settings.default_fal_image_model,
            )
        elif executor_type == "fal_video":
            return FalVideoExecutor(
                api_key=self.settings.fal_api_key,
                artifacts_dir=self.settings.artifacts_dir,
                default_model=self.settings.default_fal_video_model,
            )
        elif executor_type == "python":
            return PythonScriptExecutor(artifacts_dir=self.settings.artifacts_dir)
        else:
            return StubLLMExecutor()

    async def _get_agent_config(self, agent_name: str) -> AgentConfig | None:
        stmt = select(AgentConfig).where(AgentConfig.agent_name == agent_name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def run_agent(
        self,
        project: Project,
        agent_name: str,
        model_id: str | None = None,
        extra_params: dict | None = None,
        input_params: dict | None = None,
    ) -> dict:
        agent_def = get_agent(agent_name)
        config = await self._get_agent_config(agent_name)
        context = ProjectContext(self.db, project)

        inputs = await context.collect_inputs(agent_def.depends_on)
        run = await context.create_run(agent_name, agent_def.step, {"keys": list(inputs.keys())})

        try:
            system_prompt = (
                config.system_prompt if config and not config.is_default
                else agent_def.default_system_prompt
            )
            # Request-level overrides take priority over saved config
            model_id = model_id or (config.model_id if config else None)
            extra_params = extra_params or (config.extra_params if config else None)

            # Inject user-provided input params (e.g. selected character/scene)
            if input_params:
                inputs["user_selection"] = input_params

            executor = self._get_executor(agent_def, config)

            prompt_text = self._build_prompt(inputs)

            # Save prompt history
            history = PromptHistory(
                id=uuid.uuid4(),
                project_id=project.id,
                agent_run_id=run.id,
                agent_name=agent_name,
                system_prompt=system_prompt or "",
                user_prompt=prompt_text,
                model_id=model_id,
                extra_params=extra_params or {},
            )
            self.db.add(history)
            await self.db.flush()

            result: ExecutorResult = await executor.execute(
                prompt=prompt_text,
                inputs=inputs,
                model_id=model_id,
                system_prompt=system_prompt,
                extra_params=extra_params,
            )

            output_data = {
                "content": result.content,
                "metadata": result.metadata,
            }

            artifacts = []
            if result.content:
                try:
                    parsed = json.loads(result.content)
                    artifacts.append({
                        "name": f"{agent_name.split('.')[-1]}_output.json",
                        "type": "json",
                        "content_text": result.content,
                    })
                    output_data["parsed"] = parsed
                except json.JSONDecodeError:
                    artifacts.append({
                        "name": f"{agent_name.split('.')[-1]}_output.txt",
                        "type": "text",
                        "content_text": result.content,
                    })

            for fp in result.file_paths:
                ext = fp.rsplit(".", 1)[-1].lower()
                art_type = {"png": "png", "jpg": "image", "jpeg": "image", "mp4": "video"}.get(
                    ext, "image"
                )
                artifacts.append({
                    "name": fp.rsplit("/", 1)[-1],
                    "type": art_type,
                    "file_path": fp,
                })

            await context.complete_run(run, output_data, artifacts)
            await self.db.commit()

            logger.info(f"Agent {agent_name} completed for project {project.id}")
            return output_data

        except Exception as e:
            await context.fail_run(run, str(e))
            await self.db.commit()
            logger.error(f"Agent {agent_name} failed: {e}")
            raise

    def _build_prompt(self, inputs: dict) -> str:
        parts = []
        script = inputs.get("script", "")
        if script:
            parts.append(f"## Script\n{script[:5000]}")

        for key, value in inputs.items():
            if key == "script":
                continue
            if isinstance(value, dict):
                parts.append(
                    f"## {key}\n```json\n{json.dumps(value, ensure_ascii=False, indent=2)}\n```"
                )
            elif isinstance(value, str):
                parts.append(f"## {key}\n{value}")

        return "\n\n".join(parts) if parts else "No input provided."

    async def run_step(self, project: Project, step: int) -> list[dict]:
        agents = self.dag.agents_for_step(step)
        results = []
        for agent_name in agents:
            result = await self.run_agent(project, agent_name)
            results.append({"agent": agent_name, "result": result})
        return results

    async def run_all(self, project: Project) -> list[dict]:
        all_results = []
        for step in self.dag.steps:
            step_results = await self.run_step(project, step)
            all_results.extend(step_results)
        return all_results
