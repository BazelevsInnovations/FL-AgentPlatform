from fl_platform.agents.base import AgentDefinition, EntitySelector

setup_scene_desc_agent = AgentDefinition(
    name="location.setup_scene_desc",
    display_name="Setup Scene Description",
    department="Location Scout",
    step=14,
    executor_type="llm",
    depends_on=["location.setup_extraction", "location.isometric_image"],
    entity_selectors=[
        EntitySelector("scene", "Scene", "director.first_assistant", "location_breakdown", "scene_id"),
        EntitySelector("setup", "Setup", "location.floorplan", "setups", "name"),
    ],
    default_system_prompt="""You are creating scene descriptions for AI image generation of film frames.
You should use isometric Floorplan of a location as a guide for generation.
Your goal: describe what a person physically SEES standing at this specific spot, as if writing a paragraph for a novel. This will be used to generate a cinematic still.
RULES:
- Describe what EXISTS in the space, not how it is photographed
- Focus on: materials, textures, colors, light quality, objects, spatial depth
- Include atmosphere and emotional feel consistent with the narrative role
- Reference the isometric layout AND floorplan to ensure spatial accuracy
- Do not use isometric layout or floorplan style
- Make this generation photorealistic
- 80–120 words, present tense, immersive and specific
- Do NOT use photography or camera terminology
At the end, append a compact style tag and restrictions line:
cinematic still, [film stock/look], [dominant palette], [lighting character], [reference usage]
Return ONLY the scene description text + style tags.""",
)
