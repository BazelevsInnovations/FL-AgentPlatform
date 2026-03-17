from fl_platform.agents.base import AgentDefinition

static_shot_agent = AgentDefinition(
    name="shots.static_shot",
    display_name="Shots (Static Image)",
    department="Shots",
    step=16,
    executor_type="fal_image",
    depends_on=["shots.storyboard", "production_design.references", "location.setup_scene_gen"],
    default_system_prompt="Generate a photorealistic cinematic still frame based on storyboard reference, production design references, and location scout imagery.",
)
