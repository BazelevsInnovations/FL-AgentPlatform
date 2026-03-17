from __future__ import annotations

from fl_platform.agents.base import AgentDefinition


class PipelineDAG:
    def __init__(self, agents: dict[str, AgentDefinition]):
        self._agents = agents
        self._graph: dict[str, list[str]] = {}
        self._reverse: dict[str, list[str]] = {}
        self._build()

    def _build(self) -> None:
        for name, agent in self._agents.items():
            self._graph[name] = agent.depends_on
            self._reverse.setdefault(name, [])
            for dep in agent.depends_on:
                self._reverse.setdefault(dep, []).append(name)

    @property
    def steps(self) -> list[int]:
        return sorted({a.step for a in self._agents.values()})

    def agents_for_step(self, step: int) -> list[str]:
        return [name for name, a in self._agents.items() if a.step == step]

    def get_ready_agents(self, completed: set[str]) -> list[str]:
        ready = []
        for name, deps in self._graph.items():
            if name not in completed and all(d in completed for d in deps):
                ready.append(name)
        return ready

    def get_execution_order(self) -> list[list[str]]:
        order = []
        for step in self.steps:
            agents = self.agents_for_step(step)
            if agents:
                order.append(agents)
        return order

    def get_dependents(self, agent_name: str) -> list[str]:
        return self._reverse.get(agent_name, [])

    def get_dependencies(self, agent_name: str) -> list[str]:
        return self._graph.get(agent_name, [])

    def to_dict(self) -> dict:
        return {
            "steps": self.steps,
            "agents": {
                name: {
                    "display_name": a.display_name,
                    "department": a.department,
                    "step": a.step,
                    "depends_on": a.depends_on,
                    "executor_type": a.executor_type,
                }
                for name, a in self._agents.items()
            },
        }
