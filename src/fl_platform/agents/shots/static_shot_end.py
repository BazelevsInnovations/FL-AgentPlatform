from fl_platform.agents.base import AgentDefinition, EntitySelector, ReferenceSource

static_shot_end_agent = AgentDefinition(
    name="shots.static_shot_end",
    display_name="Shots (Last Frame)",
    department="Shots",
    step=16,
    executor_type="fal_image",
    input_description="Static shot + scene vision + DP vision",
    output_description="Last frame of video shot (optional, for start/end frame video generation)",
    depends_on=["shots.static_shot", "director.scene_vision", "cinematography.dp"],
    entity_selectors=[
        EntitySelector("shot", "Shot", "director.breakdown_table", "breakdown", "shot"),
    ],
    reference_sources=[
        ReferenceSource("first_frame_ref", "First Frame", "shots.static_shot"),
    ],
    default_system_prompt="Generate a photorealistic cinematic still frame representing the END of a video shot. This should show the final composition after the camera movement described in the DP vision. Maintain visual consistency with the first frame (static shot reference).",
)
