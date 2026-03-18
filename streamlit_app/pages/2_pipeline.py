import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

import streamlit as st
import httpx

from components.dag_graph import render_dag
from components.artifact_viewer import render_artifact

st.title("Pipeline")

API_BASE = st.session_state.get("api_base", "http://localhost:8000")
project_id = st.session_state.get("current_project_id")

if not project_id:
    project_id = st.text_input("Enter Project ID")
    if project_id:
        st.session_state["current_project_id"] = project_id

if not project_id:
    st.info("Select a project from the Projects page or enter a Project ID.")
    st.stop()

st.caption(f"Project: `{project_id}`")

try:
    dag_resp = httpx.get(f"{API_BASE}/api/v1/pipeline/dag", timeout=10)
    dag_resp.raise_for_status()
    dag_data = dag_resp.json()

    runs = {}
    try:
        for agent_name in dag_data.get("agents", {}):
            r = httpx.get(
                f"{API_BASE}/api/v1/projects/{project_id}/agents/{agent_name}/runs",
                timeout=5,
            )
            if r.status_code == 200 and r.json():
                latest = r.json()[0]
                runs[agent_name] = latest
    except Exception:
        pass

    # Load saved node positions
    saved_positions = {}
    try:
        pos_resp = httpx.get(
            f"{API_BASE}/api/v1/projects/{project_id}/pipeline/node-positions",
            timeout=5,
        )
        if pos_resp.status_code == 200:
            saved_positions = pos_resp.json()
    except Exception:
        pass

    result = render_dag(dag_data, runs, saved_positions=saved_positions)

    # Handle events from the DAG component
    clicked = None
    if result and isinstance(result, dict):
        event = result.get("event")

        if event == "click":
            clicked = result.get("node_id")

        elif event == "positions_changed":
            new_positions = result.get("positions", {})
            if new_positions:
                try:
                    httpx.put(
                        f"{API_BASE}/api/v1/projects/{project_id}/pipeline/node-positions",
                        json={"positions": new_positions},
                        timeout=5,
                    )
                except Exception:
                    pass  # Save silently; positions persist on next reload

    # Reset positions button
    if saved_positions:
        if st.button("Reset Layout", help="Reset node positions to automatic layout"):
            try:
                httpx.put(
                    f"{API_BASE}/api/v1/projects/{project_id}/pipeline/node-positions",
                    json={"positions": {}},
                    timeout=5,
                )
                st.rerun()
            except Exception as e:
                st.error(f"Failed to reset: {e}")

    # --- Controls: Run Step / Run All ---
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        step = st.number_input("Step to run", min_value=1, max_value=17, value=1)
        if st.button("Run Step"):
            with st.spinner(f"Running step {step}..."):
                resp = httpx.post(
                    f"{API_BASE}/api/v1/projects/{project_id}/pipeline/run-step",
                    json={"step": step},
                    timeout=300,
                )
                resp.raise_for_status()
                st.success(f"Step {step} completed")
                st.json(resp.json())

    with col2:
        if st.button("Run All Pipeline"):
            with st.spinner("Running full pipeline..."):
                resp = httpx.post(
                    f"{API_BASE}/api/v1/projects/{project_id}/pipeline/run-all",
                    timeout=600,
                )
                resp.raise_for_status()
                st.success("Pipeline completed")
                st.json(resp.json())

    # --- Agent Preview Panel (on node click) ---
    if clicked and clicked in dag_data.get("agents", {}):
        agent_info = dag_data["agents"][clicked]
        st.markdown("---")
        st.subheader(f"{agent_info['display_name']}")
        st.caption(f"`{clicked}` | {agent_info['department']} | Step {agent_info['step']} | Executor: {agent_info['executor_type']}")

        if agent_info.get("depends_on"):
            st.markdown(f"**Depends on:** {', '.join(agent_info['depends_on'])}")

        pcol1, pcol2 = st.columns([1, 2])

        with pcol1:
            if st.button("Run This Agent", key="run_clicked_agent"):
                with st.spinner(f"Running {agent_info['display_name']}..."):
                    try:
                        resp = httpx.post(
                            f"{API_BASE}/api/v1/projects/{project_id}/agents/{clicked}/run",
                            json={},
                            timeout=300,
                        )
                        resp.raise_for_status()
                        st.success("Completed!")
                        st.json(resp.json())
                    except Exception as e:
                        st.error(f"Error: {e}")

            if st.button("Open in Agent Detail", key="goto_agent_detail"):
                st.session_state["selected_agent"] = clicked
                st.switch_page("pages/3_agent_detail.py")

        with pcol2:
            # Show latest run result
            if clicked in runs:
                run = runs[clicked]
                st.markdown(f"**Last run:** {run['status']}")
                if run.get("error"):
                    st.error(run["error"])
                if run.get("output_data"):
                    with st.expander("Output", expanded=True):
                        st.json(run["output_data"])
            else:
                st.info("No runs yet — click 'Run This Agent' to execute.")

            # Show artifacts
            try:
                arts_resp = httpx.get(
                    f"{API_BASE}/api/v1/projects/{project_id}/artifacts",
                    params={"agent_name": clicked},
                    timeout=10,
                )
                arts_resp.raise_for_status()
                artifacts = arts_resp.json()
                if artifacts:
                    st.markdown("**Artifacts:**")
                    for art in artifacts:
                        render_artifact(art, API_BASE)
            except Exception:
                pass

except httpx.ConnectError:
    st.warning("Cannot connect to API server.")
except Exception as e:
    st.error(f"Error: {e}")
