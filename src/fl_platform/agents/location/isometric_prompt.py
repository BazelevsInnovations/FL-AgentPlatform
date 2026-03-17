from fl_platform.agents.base import AgentDefinition

isometric_prompt_agent = AgentDefinition(
    name="location.isometric_prompt",
    display_name="Isometric Reference Prompt",
    department="Location Scout",
    step=12,
    executor_type="llm",
    depends_on=["location.floorplan", "location.detail_description"],
    default_system_prompt="""You are creating an image generation prompt for an isometric illustration of a film location.
This image will serve as a shared spatial reference for the entire production team.
Using the location description and floorplan data provided, write a prompt that:
- Describes the space in isometric 3D view, showing layout, furniture, and key objects
- Specifies materials, surfaces, colors, and lighting character
- Captures the emotional atmosphere and narrative role of the space
- Uses natural descriptive language (no camera terms)
- Ends with style tags and restrictions: isometric illustration, architectural cutaway, clean linework, [dominant color palette], cinematic lighting, STRICTLY FOLLOW THE PROVIDED FLOOR PLAN.
Do not invent new furniture or alter zone positions.
Target length: 120–160 words.
Return ONLY the prompt text.""",
)
