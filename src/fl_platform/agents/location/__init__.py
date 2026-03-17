from fl_platform.agents.location.detail_description import detail_description_agent
from fl_platform.agents.location.floorplan import floorplan_agent
from fl_platform.agents.location.isometric_prompt import isometric_prompt_agent
from fl_platform.agents.location.isometric_image import isometric_image_agent
from fl_platform.agents.location.setup_extraction import setup_extraction_agent
from fl_platform.agents.location.setup_scene_desc import setup_scene_desc_agent
from fl_platform.agents.location.setup_scene_gen import setup_scene_gen_agent

LOCATION_AGENTS = [
    detail_description_agent,
    floorplan_agent,
    isometric_prompt_agent,
    isometric_image_agent,
    setup_extraction_agent,
    setup_scene_desc_agent,
    setup_scene_gen_agent,
]
