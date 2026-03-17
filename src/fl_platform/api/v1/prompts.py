from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from fl_platform.db.engine import get_db_session
from fl_platform.schemas.agent import PromptRead, PromptUpdate
from fl_platform.services import prompt_service

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("/", response_model=list[PromptRead])
async def list_prompts(db: AsyncSession = Depends(get_db_session)):
    return await prompt_service.list_prompts(db)


@router.get("/{agent_name:path}", response_model=PromptRead)
async def get_prompt(
    agent_name: str,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        return await prompt_service.get_prompt(db, agent_name)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.put("/{agent_name:path}", response_model=PromptRead)
async def update_prompt(
    agent_name: str,
    body: PromptUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        return await prompt_service.update_prompt(
            db,
            agent_name,
            system_prompt=body.system_prompt,
            model_id=body.model_id,
            extra_params=body.extra_params,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{agent_name:path}/reset", response_model=PromptRead)
async def reset_prompt(
    agent_name: str,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        return await prompt_service.reset_prompt(db, agent_name)
    except ValueError as e:
        raise HTTPException(404, str(e))
