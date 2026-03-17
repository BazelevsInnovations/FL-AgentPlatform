import streamlit as st
import httpx

st.title("Projects")

API_BASE = st.session_state.get("api_base", "http://localhost:8000")


def create_project():
    name = st.session_state.get("new_project_name", "")
    script = st.session_state.get("new_project_script", "")
    if not name:
        st.error("Enter project name")
        return
    try:
        resp = httpx.post(
            f"{API_BASE}/api/v1/projects/",
            json={"name": name, "script_text": script},
            timeout=30,
        )
        resp.raise_for_status()
        st.success(f"Project created: {resp.json()['id']}")
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")


with st.expander("Create New Project", expanded=True):
    st.text_input("Project Name", key="new_project_name")
    st.text_area("Script Text", key="new_project_script", height=200)
    st.button("Create", on_click=create_project)

st.markdown("---")
st.subheader("Existing Projects")

try:
    resp = httpx.get(f"{API_BASE}/api/v1/projects/", timeout=10)
    resp.raise_for_status()
    projects = resp.json()

    if not projects:
        st.info("No projects yet. Create one above.")
    else:
        for p in projects:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{p['name']}**")
            with col2:
                st.caption(f"Status: {p['status']} | Created: {p['created_at'][:10]}")
            with col3:
                if st.button("Open", key=f"open_{p['id']}"):
                    st.session_state["current_project_id"] = p["id"]
                    st.switch_page("pages/2_pipeline.py")

except httpx.ConnectError:
    st.warning("Cannot connect to API server. Start it with: `uvicorn fl_platform.main:app --reload`")
except Exception as e:
    st.error(f"Error loading projects: {e}")
