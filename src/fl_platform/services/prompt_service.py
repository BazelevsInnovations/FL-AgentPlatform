from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fl_platform.agents.registry import ALL_AGENTS, get_agent
from fl_platform.db.models import AgentConfig


async def get_prompt(db: AsyncSession, agent_name: str) -> dict:
    agent_def = get_agent(agent_name)

    stmt = select(AgentConfig).where(AgentConfig.agent_name == agent_name)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()

    if config:
        return {
            "agent_name": agent_name,
            "system_prompt": config.system_prompt,
            "model_id": config.model_id,
            "extra_params": config.extra_params,
            "is_default": config.is_default,
        }
    return {
        "agent_name": agent_name,
        "system_prompt": agent_def.default_system_prompt,
        "model_id": None,
        "extra_params": {},
        "is_default": True,
    }


async def update_prompt(
    db: AsyncSession,
    agent_name: str,
    system_prompt: str | None = None,
    model_id: str | None = None,
    extra_params: dict | None = None,
) -> dict:
    get_agent(agent_name)  # validate exists

    stmt = select(AgentConfig).where(AgentConfig.agent_name == agent_name)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()

    if config is None:
        agent_def = get_agent(agent_name)
        config = AgentConfig(
            id=uuid.uuid4(),
            agent_name=agent_name,
            system_prompt=system_prompt or agent_def.default_system_prompt,
            model_id=model_id,
            extra_params=extra_params or {},
            is_default=False,
        )
        db.add(config)
    else:
        if system_prompt is not None:
            config.system_prompt = system_prompt
        if model_id is not None:
            config.model_id = model_id
        if extra_params is not None:
            config.extra_params = extra_params
        config.is_default = False

    await db.commit()
    await db.refresh(config)

    return {
        "agent_name": config.agent_name,
        "system_prompt": config.system_prompt,
        "model_id": config.model_id,
        "extra_params": config.extra_params,
        "is_default": config.is_default,
    }


async def reset_prompt(db: AsyncSession, agent_name: str) -> dict:
    agent_def = get_agent(agent_name)

    stmt = select(AgentConfig).where(AgentConfig.agent_name == agent_name)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()

    if config:
        await db.delete(config)
        await db.commit()

    return {
        "agent_name": agent_name,
        "system_prompt": agent_def.default_system_prompt,
        "model_id": None,
        "extra_params": {},
        "is_default": True,
    }


async def list_prompts(db: AsyncSession) -> list[dict]:
    prompts = []
    for agent_name in ALL_AGENTS:
        prompt = await get_prompt(db, agent_name)
        prompts.append(prompt)
    return prompts
