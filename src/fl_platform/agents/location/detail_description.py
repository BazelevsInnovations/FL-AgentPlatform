from fl_platform.agents.base import AgentDefinition, EntitySelector

detail_description_agent = AgentDefinition(
    name="location.detail_description",
    display_name="Location Detail Description",
    department="Location Scout",
    step=10,
    executor_type="llm",
    depends_on=["director.first_assistant", "director.scene_vision"],
    entity_selectors=[
        EntitySelector("scene", "Scene", "director.first_assistant", "location_breakdown", "scene_id"),
    ],
    default_system_prompt="""You are a production designer filling in visual gaps for a film location.
You receive a location brief extracted from a screenplay, including a list of properties the writer did NOT describe.
Your job: invent plausible, cinematically coherent details for everything in "missingInfo", consistent with the genre, tone, era, and narrative role of this location.
For each missing property, provide:
- Your suggested value
- A 1-sentence justification based on story context
Output enriched JSON with all original fields preserved, plus new fields for each inferred property, marked "inferred: true".
Think like a production designer on a real film: specific, justified, visually rich, and consistent with the whole.""",
)
