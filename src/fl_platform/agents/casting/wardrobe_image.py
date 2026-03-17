from fl_platform.agents.base import AgentDefinition, EntitySelector

wardrobe_image_agent = AgentDefinition(
    name="casting.wardrobe_image",
    display_name="Wardrobe Image",
    department="Casting Director",
    step=5,
    executor_type="fal_image",
    input_description="Wardrobe generation prompt",
    output_description="Costume reference photo (generated image)",
    depends_on=["casting.wardrobe_gen"],
    entity_selectors=[
        EntitySelector("character", "Character", "casting.character_description", "characters", "name"),
    ],
    default_system_prompt="Generate a professional costume reference flatlay photo based on the given prompt.",
)
