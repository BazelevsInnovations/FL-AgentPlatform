from fl_platform.agents.base import AgentDefinition, EntitySelector, ReferenceSource

video_shot_agent = AgentDefinition(
    name="shots.video_shot",
    display_name="Shots (Video)",
    department="Shots",
    step=17,
    executor_type="fal_video",
    depends_on=["shots.static_shot", "cinematography.dp", "director.scene_vision", "sound.sound_director"],
    entity_selectors=[
        EntitySelector("shot", "Shot", "director.breakdown_table", "breakdown", "shot"),
    ],
    reference_sources=[
        ReferenceSource("static_ref", "Static Shot", "shots.static_shot"),
    ],
    default_system_prompt="Generate a short video clip based on DP vision (camera movement), director's scene vision, and the static shot reference image.",
)
