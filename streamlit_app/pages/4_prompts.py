import streamlit as st
import httpx

st.title("Prompt Editor")

API_BASE = st.session_state.get("api_base", "http://localhost:8000")

try:
    resp = httpx.get(f"{API_BASE}/api/v1/prompts/", timeout=10)
    resp.raise_for_status()
    prompts = resp.json()
except httpx.ConnectError:
    st.warning("Cannot connect to API server.")
    st.stop()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

agents_by_dept: dict[str, list] = {}
try:
    agents_resp = httpx.get(f"{API_BASE}/api/v1/agents", timeout=10)
    agents_resp.raise_for_status()
    for a in agents_resp.json():
        agents_by_dept.setdefault(a["department"], []).append(a)
except Exception:
    pass

prompt_map = {p["agent_name"]: p for p in prompts}

agent_names = [p["agent_name"] for p in prompts]
selected = st.selectbox("Select Agent", agent_names)

if selected and selected in prompt_map:
    p = prompt_map[selected]

    st.markdown(f"**Default:** {'Yes' if p['is_default'] else 'No (customized)'}")

    if p.get("model_id"):
        st.markdown(f"**Model:** `{p['model_id']}`")

    new_prompt = st.text_area(
        "System Prompt",
        value=p["system_prompt"],
        height=400,
        key=f"prompt_{selected}",
    )

    new_model = st.text_input(
        "Model ID (optional)",
        value=p.get("model_id") or "",
        key=f"model_{selected}",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save"):
            try:
                update_data = {"system_prompt": new_prompt}
                if new_model:
                    update_data["model_id"] = new_model
                resp = httpx.put(
                    f"{API_BASE}/api/v1/prompts/{selected}",
                    json=update_data,
                    timeout=10,
                )
                resp.raise_for_status()
                st.success("Saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        if st.button("Reset to Default"):
            try:
                resp = httpx.delete(
                    f"{API_BASE}/api/v1/prompts/{selected}/reset",
                    timeout=10,
                )
                resp.raise_for_status()
                st.success("Reset to default!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
