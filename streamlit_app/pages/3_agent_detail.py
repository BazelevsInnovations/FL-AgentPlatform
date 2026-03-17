import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

import streamlit as st
import httpx

from components.artifact_viewer import render_artifact

st.title("Agent Detail")

API_BASE = st.session_state.get("api_base", "http://localhost:8000")
project_id = st.session_state.get("current_project_id")

if not project_id:
    st.info("Select a project first.")
    st.stop()

try:
    agents_resp = httpx.get(f"{API_BASE}/api/v1/agents", timeout=10)
    agents_resp.raise_for_status()
    agents = agents_resp.json()
except Exception as e:
    st.error(f"Cannot load agents: {e}")
    st.stop()

agent_names = [a["name"] for a in agents]
agent_map = {a["name"]: a for a in agents}

default_idx = 0
preselected = st.session_state.pop("selected_agent", None)
if preselected and preselected in agent_names:
    default_idx = agent_names.index(preselected)

selected = st.selectbox(
    "Select Agent", agent_names,
    index=default_idx,
    format_func=lambda n: f"{agent_map[n]['display_name']} ({n})",
)

if selected:
    agent = agent_map[selected]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Department:** {agent['department']}")
        st.markdown(f"**Step:** {agent['step']}")
        st.markdown(f"**Executor:** {agent['executor_type']}")
    with col2:
        st.markdown(f"**Input:** {agent['input_description']}")
        st.markdown(f"**Output:** {agent['output_description']}")
        st.markdown(f"**Depends on:** {', '.join(agent['depends_on']) or '—'}")

    st.markdown("---")

    if st.button("Run Agent"):
        with st.spinner(f"Running {agent['display_name']}..."):
            try:
                resp = httpx.post(
                    f"{API_BASE}/api/v1/projects/{project_id}/agents/{selected}/run",
                    json={},
                    timeout=300,
                )
                resp.raise_for_status()
                st.success("Completed!")
                st.json(resp.json())
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("### Previous Runs")
    try:
        runs_resp = httpx.get(
            f"{API_BASE}/api/v1/projects/{project_id}/agents/{selected}/runs",
            timeout=10,
        )
        runs_resp.raise_for_status()
        runs = runs_resp.json()

        if not runs:
            st.info("No runs yet.")
        else:
            for run in runs[:5]:
                with st.expander(f"{run['status']} — {run.get('completed_at', run.get('started_at', ''))[:19]}"):
                    st.markdown(f"**Status:** {run['status']}")
                    if run.get("error"):
                        st.error(run["error"])
                    if run.get("output_data"):
                        st.json(run["output_data"])
    except Exception as e:
        st.error(f"Cannot load runs: {e}")

    st.markdown("### Artifacts")
    try:
        arts_resp = httpx.get(
            f"{API_BASE}/api/v1/projects/{project_id}/artifacts",
            params={"agent_name": selected},
            timeout=10,
        )
        arts_resp.raise_for_status()
        artifacts = arts_resp.json()

        if not artifacts:
            st.info("No artifacts yet.")
        else:
            for art in artifacts:
                render_artifact(art, API_BASE)
    except Exception as e:
        st.error(f"Cannot load artifacts: {e}")

    st.markdown("### Prompt History")
    try:
        ph_resp = httpx.get(
            f"{API_BASE}/api/v1/projects/{project_id}/agents/{selected}/prompt-history",
            timeout=10,
        )
        ph_resp.raise_for_status()
        history = ph_resp.json()

        if not history:
            st.info("No prompt history yet.")
        else:
            for entry in history:
                ts = entry.get("created_at", "")[:19]
                model = entry.get("model_id") or "default"
                with st.expander(f"{ts} — model: {model}"):
                    st.markdown("**System Prompt:**")
                    st.code(entry.get("system_prompt", ""), language=None)
                    st.markdown("**User Prompt (assembled from inputs):**")
                    st.code(entry.get("user_prompt", ""), language=None)
                    if entry.get("extra_params"):
                        st.markdown("**Extra Params:**")
                        st.json(entry["extra_params"])
    except Exception as e:
        st.error(f"Cannot load prompt history: {e}")
