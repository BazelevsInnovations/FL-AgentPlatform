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


def render_dag(dag_data: dict, runs: dict | None = None) -> str | None:
    """Render DAG and return clicked node ID (agent name) or None."""
    if not HAS_AGRAPH:
        return _render_text_dag(dag_data, runs)

    nodes = []
    edges = []

    agents = dag_data.get("agents", {})
    for name, info in agents.items():
        dept = info.get("department", "")
        color = DEPT_COLORS.get(dept, "#7F8C8D")

        if runs and name in runs:
            status = runs[name].get("status", "pending")
            color = STATUS_COLORS.get(status, color)

        label = info["display_name"]

        nodes.append(
            Node(
                id=name,
                label=label,
                size=30,
                color=color,
                title=f"{dept} | Step {info['step']}\nClick to run/view",
                font={"size": 14, "color": "#222222"},
                shape="dot",
            )
        )

        for dep in info.get("depends_on", []):
            edges.append(Edge(source=dep, target=name))

    config = Config(
        width=1400,
        height=1000,
        directed=True,
        hierarchical=True,
        physics=False,
        nodeHighlightBehavior=True,
        highlightColor="#F5A623",
        collapsible=False,
        node={"highlightStrokeColor": "#F5A623"},
        levelSeparation=120,
        nodeSpacing=200,
        treeSpacing=250,
    )

    clicked = agraph(nodes=nodes, edges=edges, config=config)
    return clicked


def _render_text_dag(dag_data: dict, runs: dict | None = None) -> str | None:
    agents = dag_data.get("agents", {})
    steps = dag_data.get("steps", [])
    clicked = None

    for step in steps:
        step_agents = {n: a for n, a in agents.items() if a["step"] == step}
        if not step_agents:
            continue

        st.markdown(f"### Step {step}")
        for name, info in step_agents.items():
            status_icon = "⬜"
            if runs and name in runs:
                s = runs[name].get("status", "pending")
                status_icon = {"completed": "✅", "running": "🔄", "failed": "❌", "pending": "⬜"}.get(s, "⬜")

            if st.button(f"{status_icon} {info['display_name']}", key=f"btn_{name}"):
                clicked = name

    return clicked
