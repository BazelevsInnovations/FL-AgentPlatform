from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EntitySelector:
    """Declarative entity selector shown in the agent runner UI."""
    key: str           # param key in input_params (e.g. "character", "scene", "shot")
    label: str         # UI label (e.g. "Character", "Scene", "Shot")
    source_agent: str  # agent that produces the list
    source_field: str  # field in output JSON containing the list
    label_field: str   # field in each list item used as display label


@dataclass
class ReferenceSource:
    """Auto-resolved reference image from a previous agent's artifacts."""
    key: str           # identifier (e.g. "face_ref")
    label: str         # UI label (e.g. "Face Portrait")
    source_agent: str  # agent whose latest image artifact to use


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
    entity_selectors: list[EntitySelector] = field(default_factory=list)
    reference_sources: list[ReferenceSource] = field(default_factory=list)
