from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class AgentInfo(BaseModel):
    name: str
    display_name: str
    department: str
    step: int
    executor_type: str
    input_description: str
    output_description: str
    depends_on: list[str]


class AgentRunRequest(BaseModel):
    model_id: str | None = None
    extra_params: dict | None = None


class AgentRunResponse(BaseModel):
    id: uuid.UUID
    agent_name: str
    step: int
    status: str
    input_data: dict
    output_data: dict
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class ArtifactResponse(BaseModel):
    id: uuid.UUID
    name: str
    artifact_type: str
    content_text: str | None
    file_path: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PromptRead(BaseModel):
    agent_name: str
    system_prompt: str
    model_id: str | None
    extra_params: dict
    is_default: bool


class PromptUpdate(BaseModel):
    system_prompt: str | None = None
    model_id: str | None = None
    extra_params: dict | None = None


class PromptHistoryResponse(BaseModel):
    id: uuid.UUID
    agent_name: str
    system_prompt: str
    user_prompt: str
    model_id: str | None
    extra_params: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class PipelineStepRequest(BaseModel):
    step: int


class PipelineStatusResponse(BaseModel):
    steps: list[int]
    agents: dict[str, dict]
    runs: dict[str, AgentRunResponse]
