from fl_platform.agents.base import AgentDefinition, EntitySelector

pd_test_shot_agent = AgentDefinition(
    name="production_design.test_shot",
    display_name="Production Designer — Test Shot",
    department="Production Designer",
    step=7,
    executor_type="llm",
    input_description="Director Film Vision JSON, Director Scene Vision JSON",
    output_description="Test Shot Prompt",
    depends_on=["director.film_vision", "director.scene_vision"],
    entity_selectors=[
        EntitySelector("shot", "Shot", "director.breakdown_table", "breakdown", "shot"),
    ],
    default_system_prompt="""You are an expert cinematographer creating test shot prompts. Create a prompt for generating a REALISTIC test shot image showing the scene environment.
The image should depict:
- The actual location/environment described in the scene
- Specific lighting conditions and time of day
- Visual mood and atmosphere of the setting
- Camera perspective that captures the space
- NO characters or people - just the empty set ready for filming
Focus on architecture, furniture, props, lighting setup, weather/atmospheric conditions. If film references are provided, incorporate their visual style.
Return ONLY the prompt text. Keep it under 150 words.""",
)
