from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentDefinition:
    name: str
    display_name: str
    department: str
    step: int
    executor_type: str  # "llm" | "fal_image" | "fal_video" | "python"
    default_system_prompt: str
    input_description: str = ""
    output_description: str = ""
    depends_on: list[str] = field(default_factory=list)
    default_model: str | None = None
