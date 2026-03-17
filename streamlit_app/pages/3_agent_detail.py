import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

import streamlit as st
import httpx

from components.artifact_viewer import render_artifact


def _render_param_controls(params_spec: dict, current_extra: dict, key_prefix: str) -> dict:
    """Render UI controls for model-specific parameters."""
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
                key=f"{key_prefix}_{param_name}", help=desc,
            )
            if val != default:
                values[param_name] = val

        elif param_type == "int":
            if default is None:
                use = st.checkbox(
                    f"Set {param_name}",
                    value=current_val is not None,
                    key=f"{key_prefix}_{param_name}_use", help=desc,
                )
                if use:
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
                    key=f"{key_prefix}_{param_name}", help=desc,
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
                key=f"{key_prefix}_{param_name}", help=desc,
            )
            if val != default:
                values[param_name] = val

        elif param_type == "bool":
            val = st.checkbox(
                param_name,
                value=bool(current_val if current_val is not None else default),
                key=f"{key_prefix}_{param_name}", help=desc,
            )
            if val != default:
                values[param_name] = val

        elif param_type == "text":
            val = st.text_input(
                param_name,
                value=str(current_val if current_val else default or ""),
                key=f"{key_prefix}_{param_name}", help=desc,
            )
            if val and val != default:
                values[param_name] = val

    return values


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

agent_map = {a["name"]: a for a in agents}

# --- Group agents by department ---
departments = sorted({a["department"] for a in agents})
dept_agents: dict[str, list[dict]] = {d: [] for d in departments}
for a in sorted(agents, key=lambda x: (x["step"], x["name"])):
    dept_agents[a["department"]].append(a)

preselected = st.session_state.pop("selected_agent", None)

# Department selector
preselected_dept = None
if preselected and preselected in agent_map:
    preselected_dept = agent_map[preselected]["department"]

dept_idx = 0
if preselected_dept and preselected_dept in departments:
    dept_idx = departments.index(preselected_dept)

selected_dept = st.selectbox("Department", departments, index=dept_idx)

# Agent selector within department
dept_agent_list = dept_agents[selected_dept]
agent_names_in_dept = [a["name"] for a in dept_agent_list]

agent_idx = 0
if preselected and preselected in agent_names_in_dept:
    agent_idx = agent_names_in_dept.index(preselected)

selected = st.selectbox(
    "Agent",
    agent_names_in_dept,
    index=agent_idx,
    format_func=lambda n: f"[Step {agent_map[n]['step']}] {agent_map[n]['display_name']} ({n})",
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

    # --- Model selector for fal_image / fal_video executors ---
    run_model_id = None
    run_extra_params = None
    executor_type = agent["executor_type"]

    if executor_type in ("fal_image", "fal_video"):
        try:
            models_resp = httpx.get(
                f"{API_BASE}/api/v1/models/{executor_type}", timeout=10,
            )
            models_resp.raise_for_status()
            models_registry = models_resp.json()
        except Exception:
            models_registry = {}

        if models_registry:
            model_ids = list(models_registry.keys())
            display_names = [
                models_registry[m].get("display", m) for m in model_ids
            ]

            st.markdown("#### Model")
            selected_model_idx = st.selectbox(
                "Select model",
                range(len(model_ids)),
                format_func=lambda i: f"{display_names[i]} ({model_ids[i]})",
                key=f"run_model_{selected}",
                label_visibility="collapsed",
            )
            run_model_id = model_ids[selected_model_idx]

            # Show model-specific parameters
            model_info = models_registry.get(run_model_id, {})
            params_spec = model_info.get("params", {})
            if params_spec:
                with st.expander("Model Parameters", expanded=False):
                    run_extra_params = _render_param_controls(
                        params_spec, {}, f"run_param_{selected}",
                    )

    # --- Input parameters: entity selection from dependency outputs ---
    run_input_params = {}
    depends_on = agent.get("depends_on", [])
    if depends_on:
        for dep_name in depends_on:
            try:
                dep_resp = httpx.get(
                    f"{API_BASE}/api/v1/projects/{project_id}/agents/{dep_name}/latest-output",
                    timeout=10,
                )
                dep_resp.raise_for_status()
                dep_output = dep_resp.json()
                if not dep_output:
                    continue

                # Look for parsed content with selectable lists
                parsed = dep_output.get("parsed") or dep_output.get("content")
                if isinstance(parsed, str):
                    try:
                        parsed = json.loads(parsed)
                    except (json.JSONDecodeError, TypeError):
                        parsed = None

                if not isinstance(parsed, dict):
                    continue

                # Find lists of entities (character_breakdown, location_breakdown, etc.)
                for list_key, items in parsed.items():
                    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
                        continue

                    # Determine label field
                    label_field = None
                    for candidate in ("name", "location_name", "scene_id", "shot"):
                        if candidate in items[0]:
                            label_field = candidate
                            break
                    if not label_field:
                        continue

                    labels = [str(item.get(label_field, f"#{i}")) for i, item in enumerate(items)]
                    labels.insert(0, f"All ({len(items)})")

                    label = list_key.replace("_", " ").title()
                    chosen = st.selectbox(
                        f"Select {label}",
                        range(len(labels)),
                        format_func=lambda i, _l=labels: _l[i],
                        key=f"input_sel_{selected}_{dep_name}_{list_key}",
                    )
                    if chosen > 0:
                        run_input_params[list_key] = items[chosen - 1]

            except Exception:
                pass

    if st.button("Run Agent"):
        body: dict = {}
        if run_model_id:
            body["model_id"] = run_model_id
        if run_extra_params:
            body["extra_params"] = run_extra_params
        if run_input_params:
            body["input_params"] = run_input_params

        with st.spinner(f"Running {agent['display_name']}..."):
            try:
                resp = httpx.post(
                    f"{API_BASE}/api/v1/projects/{project_id}/agents/{selected}/run",
                    json=body,
                    timeout=300,
                )
                resp.raise_for_status()
                st.success("Completed!")
                st.rerun()
            except httpx.HTTPStatusError as e:
                detail = ""
                try:
                    detail = e.response.json().get("detail", "")
                except Exception:
                    detail = e.response.text
                st.error(f"Error: {detail or e}")
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
