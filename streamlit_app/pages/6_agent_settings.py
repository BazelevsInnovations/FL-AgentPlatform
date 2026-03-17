import streamlit as st
import httpx

st.title("Agent Settings")

API_BASE = st.session_state.get("api_base", "http://localhost:8000")

try:
    agents_resp = httpx.get(f"{API_BASE}/api/v1/agents", timeout=10)
    agents_resp.raise_for_status()
    agents = agents_resp.json()
except httpx.ConnectError:
    st.warning("Cannot connect to API server.")
    st.stop()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

try:
    prompts_resp = httpx.get(f"{API_BASE}/api/v1/prompts/", timeout=10)
    prompts_resp.raise_for_status()
    prompts = {p["agent_name"]: p for p in prompts_resp.json()}
except Exception:
    prompts = {}

departments = sorted({a["department"] for a in agents})
selected_dept = st.selectbox("Department", ["All"] + departments)

filtered = agents if selected_dept == "All" else [a for a in agents if a["department"] == selected_dept]

for agent in sorted(filtered, key=lambda a: (a["step"], a["name"])):
    name = agent["name"]
    prompt_data = prompts.get(name, {})

    with st.expander(f"[Step {agent['step']}] {agent['display_name']} — {agent['executor_type']}"):
        st.markdown(f"**Department:** {agent['department']}")
        st.markdown(f"**Executor:** `{agent['executor_type']}`")
        st.markdown(f"**Depends on:** {', '.join(agent['depends_on']) or '—'}")

        current_model = prompt_data.get("model_id") or ""
        is_default = prompt_data.get("is_default", True)

        st.markdown(f"**Custom config:** {'No (default)' if is_default else 'Yes'}")

        new_model = st.text_input(
            "Model ID",
            value=current_model,
            key=f"settings_model_{name}",
            help="e.g. claude-sonnet-4-20250514, fal-ai/flux/dev",
        )

        if st.button("Update Model", key=f"settings_save_{name}"):
            try:
                resp = httpx.put(
                    f"{API_BASE}/api/v1/prompts/{name}",
                    json={"model_id": new_model},
                    timeout=10,
                )
                resp.raise_for_status()
                st.success(f"Model updated for {name}")
            except Exception as e:
                st.error(f"Error: {e}")
