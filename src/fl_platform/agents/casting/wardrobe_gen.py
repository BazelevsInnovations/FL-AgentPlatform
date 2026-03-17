from fl_platform.agents.base import AgentDefinition, EntitySelector

wardrobe_gen_agent = AgentDefinition(
    name="casting.wardrobe_gen",
    display_name="Wardrobe Generation",
    department="Casting Director",
    step=5,
    executor_type="llm",
    input_description="wardrobe design prompt",
    output_description="Costume photo → to Fullbody Generation",
    depends_on=["casting.wardrobe_design"],
    entity_selectors=[
        EntitySelector("character", "Character", "casting.character_description", "characters", "name"),
    ],
    default_system_prompt="""You are a film costume department photographer creating reference images.
Given a clothing/costume description, create an optimized prompt for a professional costume reference photo. Include only one outfit at a time, don't mix multiple sets of closing into a single image.
CRITICAL: Maintain historical and cultural accuracy. Use correct period-appropriate garment terminology.
Show complete outfit as a flatlay on a neutral background. Do not fold or crimple the clothing items, show them lying flat in full length/width.
Focus on: authentic period fabrics, historically accurate construction, correct colors, accessories.
Include technical terms: costume design reference, museum lighting, period-accurate, dress form display.
ALWAYS start the prompt with 'Flatlay photo of an outfit, consisting of'
Keep under 250 characters. Output ONLY the prompt.""",
)
