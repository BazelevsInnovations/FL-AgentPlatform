import streamlit as st
import httpx

from streamlit_app.components.artifact_viewer import render_artifact

st.title("Artifact Gallery")

API_BASE = st.session_state.get("api_base", "http://localhost:8000")
project_id = st.session_state.get("current_project_id")

if not project_id:
    project_id = st.text_input("Enter Project ID")

if not project_id:
    st.info("Select a project first.")
    st.stop()

filter_type = st.selectbox("Filter by type", ["all", "json", "text", "image", "png", "video"])

try:
    resp = httpx.get(
        f"{API_BASE}/api/v1/projects/{project_id}/artifacts",
        timeout=10,
    )
    resp.raise_for_status()
    artifacts = resp.json()

    if filter_type != "all":
        artifacts = [a for a in artifacts if a.get("artifact_type") == filter_type]

    if not artifacts:
        st.info("No artifacts found.")
    else:
        st.markdown(f"**{len(artifacts)} artifacts**")

        for art in artifacts:
            with st.expander(f"{art['name']} ({art['artifact_type']})"):
                render_artifact(art, API_BASE)

except httpx.ConnectError:
    st.warning("Cannot connect to API server.")
except Exception as e:
    st.error(f"Error: {e}")
