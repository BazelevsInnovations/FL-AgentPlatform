from fl_platform.agents.base import AgentDefinition, EntitySelector, ReferenceSource

static_shot_agent = AgentDefinition(
    name="shots.static_shot",
    display_name="Shots (Static Image)",
    department="Shots",
    step=16,
    executor_type="fal_image",
    depends_on=["shots.storyboard", "production_design.references", "location.setup_scene_gen"],
    entity_selectors=[
        EntitySelector("shot", "Shot", "director.breakdown_table", "breakdown", "shot"),
    ],
    reference_sources=[
        ReferenceSource("character_ref", "Character (Full Body)", "casting.fullbody_image"),
        ReferenceSource("location_ref", "Location Setup", "location.setup_scene_gen"),
    ],
    default_system_prompt="Generate a photorealistic cinematic still frame based on storyboard reference, production design references, and location scout imagery.",
)
