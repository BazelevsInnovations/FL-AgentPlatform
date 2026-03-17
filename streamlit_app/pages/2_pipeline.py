import streamlit as st
import httpx

from streamlit_app.components.dag_graph import render_dag

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

    runs_resp = httpx.get(
        f"{API_BASE}/api/v1/projects/{project_id}/artifacts",
        params={"agent_name": None},
        timeout=10,
    )

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

    render_dag(dag_data, runs)

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

except httpx.ConnectError:
    st.warning("Cannot connect to API server.")
except Exception as e:
    st.error(f"Error: {e}")
