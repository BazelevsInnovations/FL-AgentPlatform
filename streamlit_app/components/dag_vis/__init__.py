"""Custom Streamlit component for DAG visualization with draggable nodes."""

from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

_COMPONENT_DIR = Path(__file__).parent / "frontend"

_component_func = components.declare_component("dag_vis", path=str(_COMPONENT_DIR))


def dag_vis(
    nodes: list[dict],
    edges: list[dict],
    positions: dict | None = None,
    height: int = 800,
    key: str | None = None,
) -> dict | None:
    """Render an interactive DAG with VIS.js.

    Returns a dict with either:
      {"event": "click", "node_id": "..."}
      {"event": "positions_changed", "positions": {...}}
    or None if no interaction yet.
    """
    return _component_func(
        nodes=nodes,
        edges=edges,
        positions=positions or {},
        height=height,
        key=key,
        default=None,
    )
