from fl_platform.agents.base import AgentDefinition
from fl_platform.agents.director import DIRECTOR_AGENTS
from fl_platform.agents.casting import CASTING_AGENTS
from fl_platform.agents.cinematography import DP_AGENTS
from fl_platform.agents.production_design import PD_AGENTS
from fl_platform.agents.sound import SOUND_AGENTS
from fl_platform.agents.location import LOCATION_AGENTS
from fl_platform.agents.shots import SHOTS_AGENTS

ALL_AGENTS: dict[str, AgentDefinition] = {}


def _register_list(agents: list[AgentDefinition]) -> None:
    for agent in agents:
        ALL_AGENTS[agent.name] = agent


_register_list(DIRECTOR_AGENTS)
_register_list(CASTING_AGENTS)
_register_list(DP_AGENTS)
_register_list(PD_AGENTS)
_register_list(SOUND_AGENTS)
_register_list(LOCATION_AGENTS)
_register_list(SHOTS_AGENTS)


def get_agent(name: str) -> AgentDefinition:
    agent = ALL_AGENTS.get(name)
    if agent is None:
        raise ValueError(f"Unknown agent: {name}. Available: {list(ALL_AGENTS.keys())}")
    return agent


def list_agents() -> list[AgentDefinition]:
    return sorted(ALL_AGENTS.values(), key=lambda a: (a.step, a.name))


def list_departments() -> list[str]:
    return sorted({a.department for a in ALL_AGENTS.values()})
