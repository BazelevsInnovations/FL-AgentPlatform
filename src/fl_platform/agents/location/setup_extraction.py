from fl_platform.agents.base import AgentDefinition, EntitySelector

setup_extraction_agent = AgentDefinition(
    name="location.setup_extraction",
    display_name="Setup Extraction",
    department="Location Scout",
    step=13,
    executor_type="llm",
    depends_on=["location.floorplan"],
    entity_selectors=[
        EntitySelector("scene", "Scene", "director.first_assistant", "location_breakdown", "scene_id"),
    ],
    default_system_prompt="""You are a professional production designer analyzing a screenplay.
Identify specific physical spots/areas within the location where action takes place.
A "setup" is a concrete part of the space — not a camera angle.
Examples: "Kitchen Window", "Bar Counter", "Office Door".
For each setup describe:
- Physical objects, surfaces, materials
- Lighting conditions and sources
- Colors, textures, visible wear or age
- Atmosphere and emotional quality
- Spatial depth (foreground / middle / background elements)
- Human scale: how a person relates to this space (cramped, exposed, dwarfed, intimate)
- Narrative weight: what dramatically happens at this spot
Format: Area name — rich description (4–6 sentences per setup).
Make a list of 4-10 setup, depending on location size""",
)
