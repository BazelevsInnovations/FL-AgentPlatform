import streamlit as st
import httpx

st.title("Agent Settings")

API_BASE = st.session_state.get("api_base", "http://localhost:8000")

# Available models grouped by executor type
LLM_MODELS = [
    "claude-sonnet-4-20250514",
    "claude-opus-4-20250514",
    "claude-haiku-4-5-20251001",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "o1",
    "o1-mini",
]

FAL_IMAGE_MODELS = [
    "fal-ai/flux/dev",
    "fal-ai/flux-pro/v1.1-ultra",
    "fal-ai/flux-realism",
    "fal-ai/stable-diffusion-v35-large",
    "fal-ai/recraft-v3",
    "fal-ai/ideogram/v2/turbo",
]

FAL_VIDEO_MODELS = [
    "fal-ai/minimax/video-01-live",
    "fal-ai/kling-video/v2/master",
    "fal-ai/runway-gen3/turbo",
    "fal-ai/luma-dream-machine",
    "fal-ai/hunyuan-video",
]

MODELS_BY_EXECUTOR = {
    "llm": LLM_MODELS,
    "fal_image": FAL_IMAGE_MODELS,
    "fal_video": FAL_VIDEO_MODELS,
    "python": [],
}

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
    executor_type = agent["executor_type"]
    prompt_data = prompts.get(name, {})

    with st.expander(f"[Step {agent['step']}] {agent['display_name']} — {executor_type}"):
        st.markdown(f"**Department:** {agent['department']}")
        st.markdown(f"**Executor:** `{executor_type}`")
        st.markdown(f"**Depends on:** {', '.join(agent['depends_on']) or '—'}")

        current_model = prompt_data.get("model_id") or ""
        is_default = prompt_data.get("is_default", True)

        st.markdown(f"**Custom config:** {'No (default)' if is_default else 'Yes'}")

        available_models = MODELS_BY_EXECUTOR.get(executor_type, [])

        if available_models:
            # Build options: available models + current if custom + "Custom..."
            options = list(available_models)
            if current_model and current_model not in options:
                options.insert(0, current_model)
            options.append("Custom...")

            current_idx = 0
            if current_model in options:
                current_idx = options.index(current_model)

            selected_model = st.selectbox(
                "Model",
                options,
                index=current_idx,
                key=f"settings_model_{name}",
            )

            if selected_model == "Custom...":
                selected_model = st.text_input(
                    "Enter custom model ID",
                    value=current_model,
                    key=f"settings_custom_model_{name}",
                )
        else:
            selected_model = st.text_input(
                "Model ID",
                value=current_model,
                key=f"settings_model_{name}",
                help="No predefined models for this executor type",
            )

        if st.button("Update Model", key=f"settings_save_{name}"):
            try:
                resp = httpx.put(
                    f"{API_BASE}/api/v1/prompts/{name}",
                    json={"model_id": selected_model},
                    timeout=10,
                )
                resp.raise_for_status()
                st.success(f"Model updated for {name}")
            except Exception as e:
                st.error(f"Error: {e}")
