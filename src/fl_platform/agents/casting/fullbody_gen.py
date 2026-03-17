from fl_platform.agents.base import AgentDefinition, EntitySelector

fullbody_gen_agent = AgentDefinition(
    name="casting.fullbody_gen",
    display_name="Fullbody Generation",
    department="Casting Director",
    step=5,
    executor_type="llm",
    input_description="Portrait + Wardrobe",
    output_description="Character Fullbody photo → to static shot generation",
    depends_on=["casting.portrait_gen", "casting.wardrobe_gen"],
    entity_selectors=[
        EntitySelector("character", "Character", "casting.character_description", "characters", "name"),
    ],
    default_system_prompt="""You are an expert at creating prompts for AI full-body portrait generation.
Given face, wardrobe and in-script descriptions, create an optimized prompt for a professional full-body portrait photo.
Show a person with described features wearing the described outfit.
Focus on: pose, lighting, full body composition, character expression.
Include technical terms: full body shot, professional studio, cinematic lighting; visible skin, hair and fabric textures; neutral pose, standing straight, looking at the camera.
ALWAYS start the prompt with 'Full-body photo of'. Make sure all of the clothing items from the wardrobe reference are included, and any extra attributes of the character mentioned in the script. Exclude 'black t-shirt' from the face portrait prompt input.
Keep under 250 characters. Output ONLY the prompt.""",
)
