from fl_platform.agents.registry import ALL_AGENTS, get_agent, list_agents, list_departments


def test_all_agents_registered():
    assert len(ALL_AGENTS) > 0
    assert len(ALL_AGENTS) >= 20


def test_list_agents_sorted_by_step():
    agents = list_agents()
    steps = [a.step for a in agents]
    assert steps == sorted(steps)


def test_get_agent_valid():
    agent = get_agent("director.script_brief")
    assert agent.name == "director.script_brief"
    assert agent.department == "Director"
    assert agent.step == 2


def test_get_agent_invalid():
    try:
        get_agent("nonexistent.agent")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_list_departments():
    departments = list_departments()
    assert "Director" in departments
    assert "Casting Director" in departments
    assert "DP" in departments


def test_all_agents_have_system_prompt():
    for name, agent in ALL_AGENTS.items():
        assert agent.default_system_prompt, f"Agent {name} has no system prompt"


def test_agent_dependencies_exist():
    for name, agent in ALL_AGENTS.items():
        for dep in agent.depends_on:
            assert dep in ALL_AGENTS, f"Agent {name} depends on unknown agent {dep}"


def test_steps_coverage():
    steps = {a.step for a in ALL_AGENTS.values()}
    assert 1 in steps
    assert 2 in steps
    assert 3 in steps
    assert 4 in steps
    assert 5 in steps
