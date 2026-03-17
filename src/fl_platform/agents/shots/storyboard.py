from fl_platform.agents.base import AgentDefinition

storyboard_agent = AgentDefinition(
    name="shots.storyboard",
    display_name="Storyboard Artist",
    department="Storyboard Artist",
    step=15,
    executor_type="fal_image",
    depends_on=["director.scene_vision", "cinematography.dp"],
    default_system_prompt="Generate a storyboard frame based on Director Scene Vision and DP Vision. Black and white sketch style, clear composition showing camera angle, character positions, and key action.",
)
