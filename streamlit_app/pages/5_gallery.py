import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import httpx
from datetime import datetime, timezone

from components.artifact_viewer import render_artifact, render_artifact_metadata

st.title("Artifact Gallery")

API_BASE = st.session_state.get("api_base", "http://localhost:8000")
project_id = st.session_state.get("current_project_id")

if not project_id:
    project_id = st.text_input("Enter Project ID")

if not project_id:
    st.info("Select a project first.")
    st.stop()

# ── Sidebar filters ──────────────────────────────────────────────────────────

st.sidebar.header("Gallery Filters")

# Fetch filter options
try:
    filters_resp = httpx.get(
        f"{API_BASE}/api/v1/projects/{project_id}/gallery/filters",
        timeout=10,
    )
    filters_resp.raise_for_status()
    filter_opts = filters_resp.json()
except Exception:
    filter_opts = {"artifact_types": [], "agent_names": [], "steps": [], "departments": []}

# Type filter
type_options = ["all"] + filter_opts.get("artifact_types", [])
filter_type = st.sidebar.selectbox("Type", type_options)

# Department filter
dept_options = ["all"] + filter_opts.get("departments", [])
filter_dept = st.sidebar.selectbox("Department", dept_options)

# Agent filter
agent_options = ["all"] + filter_opts.get("agent_names", [])
filter_agent = st.sidebar.selectbox("Agent", agent_options)

# Step filter
step_options = ["all"] + [str(s) for s in filter_opts.get("steps", [])]
filter_step = st.sidebar.selectbox("Pipeline Step", step_options)

# Sort
sort_option = st.sidebar.selectbox(
    "Sort by",
    ["Newest first", "Oldest first", "By step", "By agent"],
)

# View mode
DEPT_ICONS = {
    "Director": "🎬",
    "Casting": "🎭",
    "Cinematography": "📷",
    "Production Design": "🎨",
    "Sound": "🎵",
    "Location": "📍",
    "Shots": "🎞️",
}

# ── Fetch gallery data ───────────────────────────────────────────────────────

params: dict = {}
if filter_type != "all":
    params["artifact_type"] = filter_type
if filter_agent != "all":
    params["agent_name"] = filter_agent
if filter_step != "all":
    params["step"] = int(filter_step)
if filter_dept != "all":
    params["department"] = filter_dept

try:
    resp = httpx.get(
        f"{API_BASE}/api/v1/projects/{project_id}/gallery",
        params=params,
        timeout=15,
    )
    resp.raise_for_status()
    artifacts = resp.json()
except httpx.ConnectError:
    st.warning("Cannot connect to API server.")
    st.stop()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

# ── Sort ──────────────────────────────────────────────────────────────────────

if sort_option == "Oldest first":
    artifacts.sort(key=lambda a: a.get("created_at", ""))
elif sort_option == "By step":
    artifacts.sort(key=lambda a: (a.get("step", 0), a.get("created_at", "")))
elif sort_option == "By agent":
    artifacts.sort(key=lambda a: (a.get("agent_display_name", ""), a.get("created_at", "")))
# "Newest first" is default from API


if not artifacts:
    st.info("No artifacts found for the selected filters.")
    st.stop()

# ── Stats bar ─────────────────────────────────────────────────────────────────

total = len(artifacts)
images = sum(1 for a in artifacts if a.get("artifact_type") in ("image", "png"))
videos = sum(1 for a in artifacts if a.get("artifact_type") == "video")
texts = sum(1 for a in artifacts if a.get("artifact_type") in ("json", "text"))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", total)
col2.metric("Images", images)
col3.metric("Videos", videos)
col4.metric("Text/JSON", texts)

st.divider()

# ── Render: grid for images/video, list for text/json ─────────────────────────

# Separate visual (image/video) from text artifacts
visual_artifacts = [a for a in artifacts if a.get("artifact_type") in ("image", "png", "video")]
text_artifacts = [a for a in artifacts if a.get("artifact_type") in ("json", "text")]


def _relative_time(iso_str: str | None) -> str:
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - dt
        seconds = delta.total_seconds()
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            mins = int(seconds / 60)
            return f"{mins}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        else:
            days = int(seconds / 86400)
            return f"{days}d ago"
    except Exception:
        return ""


def _render_card_header(art: dict) -> None:
    """Render compact metadata header for an artifact card."""
    dept = art.get("department", "")
    icon = DEPT_ICONS.get(dept, "")
    display = art.get("agent_display_name", art.get("agent_name", ""))
    model = art.get("model_id") or ""
    step = art.get("step", "")
    time_str = _relative_time(art.get("created_at"))

    st.caption(
        f"{icon} **{display}** · Step {step} · {dept}"
        + (f" · `{model}`" if model else "")
        + (f" · {time_str}" if time_str else "")
    )


# ── Visual artifacts (grid) ──────────────────────────────────────────────────

if visual_artifacts:
    st.subheader(f"Visual Resources ({len(visual_artifacts)})")

    COLS = 3
    for i in range(0, len(visual_artifacts), COLS):
        cols = st.columns(COLS)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(visual_artifacts):
                break
            art = visual_artifacts[idx]
            with col:
                _render_card_header(art)
                render_artifact(art, API_BASE)
                with st.expander("Details"):
                    render_artifact_metadata(art, API_BASE)

# ── Text/JSON artifacts (list) ───────────────────────────────────────────────

if text_artifacts:
    st.subheader(f"Text & Data Resources ({len(text_artifacts)})")

    for art in text_artifacts:
        name = art.get("name", "unknown")
        art_type = art.get("artifact_type", "")
        dept = art.get("department", "")
        icon = DEPT_ICONS.get(dept, "")
        display = art.get("agent_display_name", art.get("agent_name", ""))
        time_str = _relative_time(art.get("created_at"))

        header = f"{icon} {name} ({art_type}) — {display}"
        if time_str:
            header += f" · {time_str}"

        with st.expander(header):
            _render_card_header(art)
            render_artifact(art, API_BASE)
            st.divider()
            render_artifact_metadata(art, API_BASE)
