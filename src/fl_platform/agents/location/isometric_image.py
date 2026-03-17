from fl_platform.agents.base import AgentDefinition, EntitySelector

isometric_image_agent = AgentDefinition(
    name="location.isometric_image",
    display_name="Isometric Reference Image",
    department="Location Scout",
    step=12,
    executor_type="fal_image",
    depends_on=["location.isometric_prompt", "location.floorplan"],
    entity_selectors=[
        EntitySelector("scene", "Scene", "director.first_assistant", "location_breakdown", "scene_id"),
    ],
    default_system_prompt="""You are creating an image of an isometric illustration of a film location.
This image will serve as a shared spatial reference for the entire production team.
Image should NOT be in style of the floor plan.
Image SHOULD HAVE identified "setup" spots with a numbered circle, as on the floorplan reference""",
)
