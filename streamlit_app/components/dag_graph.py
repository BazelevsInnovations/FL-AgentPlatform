from __future__ import annotations

import streamlit as st

from components.dag_vis import dag_vis

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


def render_dag(
    dag_data: dict,
    runs: dict | None = None,
    saved_positions: dict | None = None,
) -> dict | None:
    """Render DAG and return interaction event dict or None.

    Returns:
        {"event": "click", "node_id": "..."} on node click
        {"event": "positions_changed", "positions": {...}} on drag end
        None if no interaction
    """
    agents = dag_data.get("agents", {})

    nodes = []
    edges = []

    for name, info in agents.items():
        dept = info.get("department", "")
        color = DEPT_COLORS.get(dept, "#7F8C8D")

        if runs and name in runs:
            status = runs[name].get("status", "pending")
            color = STATUS_COLORS.get(status, color)

        nodes.append({
            "id": name,
            "label": info["display_name"],
            "color": color,
            "size": 30,
            "title": f"{dept} | Step {info['step']}\nDrag to reposition",
            "level": info["step"],
        })

        for dep in info.get("depends_on", []):
            edges.append({"from": dep, "to": name})

    result = dag_vis(
        nodes=nodes,
        edges=edges,
        positions=saved_positions or {},
        height=800,
        key="pipeline_dag",
    )

    return result
