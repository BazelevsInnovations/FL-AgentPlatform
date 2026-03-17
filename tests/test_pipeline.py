from fl_platform.agents.registry import ALL_AGENTS
from fl_platform.pipeline.dag import PipelineDAG


def test_dag_creation():
    dag = PipelineDAG(ALL_AGENTS)
    assert len(dag.steps) > 0


def test_dag_execution_order():
    dag = PipelineDAG(ALL_AGENTS)
    order = dag.get_execution_order()
    assert len(order) > 0
    assert isinstance(order[0], list)


def test_dag_step_agents():
    dag = PipelineDAG(ALL_AGENTS)
    step1 = dag.agents_for_step(1)
    assert "director.first_assistant" in step1


def test_dag_ready_agents():
    dag = PipelineDAG(ALL_AGENTS)
    ready = dag.get_ready_agents(set())
    assert "director.first_assistant" in ready


def test_dag_ready_after_step1():
    dag = PipelineDAG(ALL_AGENTS)
    completed = {"director.first_assistant"}
    ready = dag.get_ready_agents(completed)
    assert "director.script_brief" in ready
    assert "director.first_assistant" not in ready


def test_dag_to_dict():
    dag = PipelineDAG(ALL_AGENTS)
    d = dag.to_dict()
    assert "steps" in d
    assert "agents" in d
    assert "director.first_assistant" in d["agents"]


def test_dag_dependencies():
    dag = PipelineDAG(ALL_AGENTS)
    deps = dag.get_dependencies("director.scene_vision")
    assert "director.film_vision" in deps


def test_dag_dependents():
    dag = PipelineDAG(ALL_AGENTS)
    dependents = dag.get_dependents("director.first_assistant")
    assert len(dependents) > 0
