from fl_platform.agents.director.first_assistant import first_assistant_agent
from fl_platform.agents.director.script_brief import script_brief_agent
from fl_platform.agents.director.breakdown_table import breakdown_table_agent
from fl_platform.agents.director.film_vision import film_vision_agent
from fl_platform.agents.director.scene_vision import scene_vision_agent

DIRECTOR_AGENTS = [
    first_assistant_agent,
    script_brief_agent,
    breakdown_table_agent,
    film_vision_agent,
    scene_vision_agent,
]
