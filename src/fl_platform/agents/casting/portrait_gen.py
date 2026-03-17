from fl_platform.agents.base import AgentDefinition

portrait_gen_agent = AgentDefinition(
    name="casting.portrait_gen",
    display_name="Portrait Generation",
    department="Casting Director",
    step=5,
    executor_type="llm",
    input_description="face prompt",
    output_description="Character Portrait photo → to Fullbody Generation",
    depends_on=["casting.character_description"],
    default_system_prompt="""You are an expert at creating prompts for AI portrait image generation.
Given a character description, create an optimized prompt for generating a professional cinematic portrait photo. Account for fitting bodytype, weight category, level of conventional attractiveness according to the script.
Focus on: facial features, expression, lighting, and atmosphere. Include the description of the character's vibe, distinctive facial features and overall face geometry.
Include technical terms: studio lighting, cinematic, professional portrait, visible skin texture, hair texture.
ALWAYS start the prompt with 'Portrait photo shot of'. Exclude external objects in the photo. Make sure that the character's head is fully visible, including their entire hairstyle. The character must be wearing a black blank t-shirt in the portrait.
Keep the prompt under 200 characters. Output ONLY the prompt.""",
)
