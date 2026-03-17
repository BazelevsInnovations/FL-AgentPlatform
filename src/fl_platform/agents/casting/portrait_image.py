from fl_platform.agents.base import AgentDefinition, EntitySelector

portrait_image_agent = AgentDefinition(
    name="casting.portrait_image",
    display_name="Portrait Image",
    department="Casting Director",
    step=5,
    executor_type="fal_image",
    input_description="Portrait generation prompt",
    output_description="Character Portrait photo (generated image)",
    depends_on=["casting.portrait_gen"],
    entity_selectors=[
        EntitySelector("character", "Character", "casting.character_description", "characters", "name"),
    ],
    default_system_prompt="Generate a professional cinematic portrait photo based on the given prompt.",
)
