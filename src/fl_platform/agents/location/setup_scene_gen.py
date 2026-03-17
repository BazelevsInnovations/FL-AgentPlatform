from fl_platform.agents.base import AgentDefinition, EntitySelector

setup_scene_gen_agent = AgentDefinition(
    name="location.setup_scene_gen",
    display_name="Setup Scene Generation",
    department="Location Scout",
    step=14,
    executor_type="fal_image",
    depends_on=["location.setup_scene_desc", "location.isometric_image"],
    entity_selectors=[
        EntitySelector("scene", "Scene", "director.first_assistant", "location_breakdown", "scene_id"),
        EntitySelector("setup", "Setup", "location.floorplan", "setups", "name"),
    ],
    default_system_prompt="Generate a photorealistic cinematic still of a film location setup based on the scene description provided.",
)
