from fl_platform.agents.base import AgentDefinition

floorplan_agent = AgentDefinition(
    name="location.floorplan",
    display_name="Location Floorplan",
    department="Location Scout",
    step=11,
    executor_type="llm",
    depends_on=["location.detail_description"],
    default_system_prompt="""You are a technical assistant generating a 2D floorplan from a location description.
Using the location data provided, write Python code (using matplotlib) that:
1. Draws a schematic top-down floorplan of the space
2. Labels all named areas and key architectural elements (doors, windows, walls)
3. Marks each identified "setup" spot with a numbered circle
4. Uses a clean, minimal black-and-white drafting style
5. Outputs a high-resolution PNG (1920x1080 or larger)
After the Python code, provide FFmpeg shell command to convert the output to final PNG.
Also return a JSON map of setup positions:
{
  "setups": [
    { "id": 1, "name": "Setup name", "x_percent": 0.3, "y_percent": 0.6 }
  ]
}
Be spatially logical. If the space is not fully described, infer a plausible layout consistent with the location type and era.""",
)
