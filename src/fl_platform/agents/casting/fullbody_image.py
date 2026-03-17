from fl_platform.agents.base import AgentDefinition

fullbody_image_agent = AgentDefinition(
    name="casting.fullbody_image",
    display_name="Fullbody Image",
    department="Casting Director",
    step=5,
    executor_type="fal_image",
    input_description="Fullbody prompt + portrait image ref + wardrobe image ref",
    output_description="Character full-body photo (generated image with face and wardrobe references)",
    depends_on=["casting.fullbody_gen", "casting.portrait_image", "casting.wardrobe_image"],
    default_system_prompt="Generate a professional full-body character photo combining the face reference and wardrobe reference.",
)
