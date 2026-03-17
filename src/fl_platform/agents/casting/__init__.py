from fl_platform.agents.casting.character_description import character_description_agent
from fl_platform.agents.casting.portrait_gen import portrait_gen_agent
from fl_platform.agents.casting.portrait_image import portrait_image_agent
from fl_platform.agents.casting.wardrobe_design import wardrobe_design_agent
from fl_platform.agents.casting.wardrobe_gen import wardrobe_gen_agent
from fl_platform.agents.casting.wardrobe_image import wardrobe_image_agent
from fl_platform.agents.casting.fullbody_gen import fullbody_gen_agent
from fl_platform.agents.casting.fullbody_image import fullbody_image_agent

CASTING_AGENTS = [
    character_description_agent,
    portrait_gen_agent,
    portrait_image_agent,
    wardrobe_design_agent,
    wardrobe_gen_agent,
    wardrobe_image_agent,
    fullbody_gen_agent,
    fullbody_image_agent,
]
