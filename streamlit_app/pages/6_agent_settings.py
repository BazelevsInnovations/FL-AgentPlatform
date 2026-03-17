import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".." / "src"))

import streamlit as st
import httpx

from fl_platform.models_registry import get_models_for_executor

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


def render_param_controls(params_spec: dict, current_extra: dict, key_prefix: str) -> dict:
    """Render UI controls for model-specific parameters. Returns dict of param values."""
    values = {}
    for param_name, spec in params_spec.items():
        param_type = spec["type"]
        default = spec.get("default")
        current_val = current_extra.get(param_name, default)
        desc = spec.get("description", "")

        if param_type == "select":
            options = spec["options"]
            idx = 0
            if current_val in options:
                idx = options.index(current_val)
            val = st.selectbox(
                param_name, options, index=idx,
                key=f"{key_prefix}_{param_name}",
                help=desc,
            )
            if val != default:
                values[param_name] = val

        elif param_type == "int":
            if default is None:
                use_seed = st.checkbox(
                    f"Set {param_name}",
                    value=current_val is not None,
                    key=f"{key_prefix}_{param_name}_use",
                    help=desc,
                )
                if use_seed:
                    val = st.number_input(
                        param_name,
                        min_value=spec.get("min", 0),
                        max_value=spec.get("max", 999999),
                        value=current_val if current_val is not None else 0,
                        key=f"{key_prefix}_{param_name}",
                    )
                    values[param_name] = int(val)
            else:
                val = st.number_input(
                    param_name,
                    min_value=spec.get("min", 0),
                    max_value=spec.get("max", 999999),
                    value=current_val if current_val is not None else default,
                    key=f"{key_prefix}_{param_name}",
                    help=desc,
                )
                if val != default:
                    values[param_name] = int(val)

        elif param_type == "float":
            val = st.slider(
                param_name,
                min_value=float(spec.get("min", 0)),
                max_value=float(spec.get("max", 1)),
                value=float(current_val if current_val is not None else default),
                step=0.05,
                key=f"{key_prefix}_{param_name}",
                help=desc,
            )
            if val != default:
                values[param_name] = val

        elif param_type == "bool":
            val = st.checkbox(
                param_name,
                value=bool(current_val if current_val is not None else default),
                key=f"{key_prefix}_{param_name}",
                help=desc,
            )
            if val != default:
                values[param_name] = val

        elif param_type == "text":
            val = st.text_input(
                param_name,
                value=str(current_val if current_val else default or ""),
                key=f"{key_prefix}_{param_name}",
                help=desc,
            )
            if val and val != default:
                values[param_name] = val

    return values


for agent in sorted(filtered, key=lambda a: (a["step"], a["name"])):
    name = agent["name"]
    executor_type = agent["executor_type"]
    prompt_data = prompts.get(name, {})

    with st.expander(f"[Step {agent['step']}] {agent['display_name']} — {executor_type}"):
        st.markdown(f"**Department:** {agent['department']}")
        st.markdown(f"**Executor:** `{executor_type}`")
        st.markdown(f"**Depends on:** {', '.join(agent['depends_on']) or '—'}")

        current_model = prompt_data.get("model_id") or ""
        current_extra = prompt_data.get("extra_params") or {}
        is_default = prompt_data.get("is_default", True)

        st.markdown(f"**Custom config:** {'No (default)' if is_default else 'Yes'}")

        models_registry = get_models_for_executor(executor_type)

        if models_registry:
            model_ids = list(models_registry.keys())
            display_names = [models_registry[m].get("display", m) for m in model_ids]

            # Add current model if custom
            if current_model and current_model not in model_ids:
                model_ids.insert(0, current_model)
                display_names.insert(0, f"{current_model} (custom)")

            model_ids.append("__custom__")
            display_names.append("Custom...")

            current_idx = 0
            if current_model in model_ids:
                current_idx = model_ids.index(current_model)

            selected_idx = st.selectbox(
                "Model",
                range(len(model_ids)),
                index=current_idx,
                format_func=lambda i: display_names[i],
                key=f"settings_model_{name}",
            )
            selected_model_id = model_ids[selected_idx]

            if selected_model_id == "__custom__":
                selected_model_id = st.text_input(
                    "Enter custom model ID",
                    value=current_model,
                    key=f"settings_custom_model_{name}",
                )
                extra_params = current_extra
            else:
                # Show model-specific parameters
                model_info = models_registry.get(selected_model_id, {})
                params_spec = model_info.get("params", {})
                if params_spec:
                    st.markdown("**Model Parameters:**")
                    extra_params = render_param_controls(
                        params_spec, current_extra, f"param_{name}"
                    )
                else:
                    extra_params = current_extra
        else:
            selected_model_id = st.text_input(
                "Model ID",
                value=current_model,
                key=f"settings_model_{name}",
                help="No predefined models for this executor type",
            )
            extra_params = current_extra

        if st.button("Save Settings", key=f"settings_save_{name}"):
            try:
                payload = {"model_id": selected_model_id}
                if extra_params:
                    payload["extra_params"] = extra_params
                resp = httpx.put(
                    f"{API_BASE}/api/v1/prompts/{name}",
                    json=payload,
                    timeout=10,
                )
                resp.raise_for_status()
                st.success(f"Settings saved for {agent['display_name']}")
            except Exception as e:
                st.error(f"Error: {e}")
