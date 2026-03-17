from __future__ import annotations

import streamlit as st

try:
    from streamlit_agraph import agraph, Node, Edge, Config
    HAS_AGRAPH = True
except ImportError:
    HAS_AGRAPH = False


DEPT_COLORS = {
    "Director": "#4A90D9",
    "Casting Director": "#E67E22",
    "DP": "#2ECC71",
    "Production Designer": "#9B59B6",
    "Sound Director": "#E74C3C",
    "Location Scout": "#1ABC9C",
    "Storyboard Artist": "#F39C12",
    "Shots": "#34495E",
}

STATUS_COLORS = {
    "completed": "#2ECC71",
    "running": "#F39C12",
    "failed": "#E74C3C",
    "pending": "#95A5A6",
}


def render_dag(dag_data: dict, runs: dict | None = None) -> None:
    if not HAS_AGRAPH:
        _render_text_dag(dag_data, runs)
        return

    nodes = []
    edges = []

    agents = dag_data.get("agents", {})
    for name, info in agents.items():
        dept = info.get("department", "")
        color = DEPT_COLORS.get(dept, "#7F8C8D")

        if runs and name in runs:
            status = runs[name].get("status", "pending")
            color = STATUS_COLORS.get(status, color)

        nodes.append(
            Node(
                id=name,
                label=f"[{info['step']}] {info['display_name']}",
                size=20,
                color=color,
                title=f"{dept} | Step {info['step']}",
            )
        )

        for dep in info.get("depends_on", []):
            edges.append(Edge(source=dep, target=name))

    config = Config(
        width=1200,
        height=800,
        directed=True,
        hierarchical=True,
        physics=False,
        nodeHighlightBehavior=True,
    )

    agraph(nodes=nodes, edges=edges, config=config)


def _render_text_dag(dag_data: dict, runs: dict | None = None) -> None:
    agents = dag_data.get("agents", {})
    steps = dag_data.get("steps", [])

    for step in steps:
        step_agents = {n: a for n, a in agents.items() if a["step"] == step}
        if not step_agents:
            continue

        st.markdown(f"### Step {step}")
        for name, info in step_agents.items():
            status = "⬜"
            if runs and name in runs:
                s = runs[name].get("status", "pending")
                status = {"completed": "✅", "running": "🔄", "failed": "❌", "pending": "⬜"}.get(s, "⬜")

            deps = ", ".join(info.get("depends_on", [])) or "—"
            st.markdown(
                f"{status} **{info['display_name']}** (`{name}`) "
                f"| {info['department']} | deps: {deps}"
            )
