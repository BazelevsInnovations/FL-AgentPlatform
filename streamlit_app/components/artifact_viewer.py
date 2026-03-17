from __future__ import annotations

import json

import pandas as pd
import streamlit as st


def render_artifact(artifact: dict, api_base: str) -> None:
    """Render the artifact content (image, video, json, text)."""
    art_type = artifact.get("artifact_type", "")
    name = artifact.get("name", "unknown")

    if art_type in ("json", "text"):
        content = artifact.get("content_text", "")
        if art_type == "json":
            try:
                parsed = json.loads(content)
                _render_json_smart(parsed, name)
            except json.JSONDecodeError:
                st.code(content)
        else:
            st.text(content)

    elif art_type in ("image", "png"):
        file_path = artifact.get("file_path", "")
        if file_path:
            try:
                st.image(file_path, caption=name, use_container_width=True)
            except Exception:
                artifact_id = artifact.get("id", "")
                project_id = artifact.get("project_id", "")
                download_url = f"{api_base}/api/v1/projects/{project_id}/artifacts/{artifact_id}/download"
                st.markdown(f"[Download image]({download_url})")

    elif art_type == "video":
        file_path = artifact.get("file_path", "")
        if file_path:
            try:
                st.video(file_path)
            except Exception:
                st.info(f"Video file: {file_path}")

    else:
        st.text(f"Unknown type: {art_type}")


def _render_json_smart(data, name: str) -> None:
    """Render JSON data: arrays of dicts as tables, everything else as json."""
    if isinstance(data, list) and data and isinstance(data[0], dict):
        st.markdown(f"**{name}**")
        st.dataframe(pd.DataFrame(data), use_container_width=True)
        return

    if isinstance(data, dict):
        has_tables = False
        remainder = {}
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                has_tables = True
                st.markdown(f"**{key}**")
                st.dataframe(pd.DataFrame(value), use_container_width=True)
            else:
                remainder[key] = value

        if remainder:
            if has_tables:
                with st.expander("Other data"):
                    st.json(remainder)
            else:
                st.json(data)
        return

    st.json(data)


def render_artifact_metadata(artifact: dict, api_base: str) -> None:
    """Render detailed metadata block for a gallery artifact."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Agent**")
        display_name = artifact.get("agent_display_name", artifact.get("agent_name", "—"))
        agent_name = artifact.get("agent_name", "")
        st.text(f"{display_name}")
        if agent_name and agent_name != display_name:
            st.caption(f"`{agent_name}`")

        st.markdown("**Department**")
        st.text(artifact.get("department", "—"))

        st.markdown("**Pipeline Step**")
        st.text(str(artifact.get("step", "—")))

    with col2:
        st.markdown("**Model**")
        st.text(artifact.get("model_id") or "—")

        st.markdown("**Run Status**")
        status = artifact.get("run_status", "—")
        if status == "completed":
            st.success(status)
        elif status == "failed":
            st.error(status)
        else:
            st.text(status)

        st.markdown("**Created**")
        created = artifact.get("created_at", "—")
        st.text(str(created))

        if artifact.get("started_at") and artifact.get("completed_at"):
            st.markdown("**Duration**")
            try:
                from datetime import datetime
                start = datetime.fromisoformat(artifact["started_at"])
                end = datetime.fromisoformat(artifact["completed_at"])
                delta = end - start
                seconds = delta.total_seconds()
                if seconds < 60:
                    st.text(f"{seconds:.1f}s")
                else:
                    st.text(f"{int(seconds // 60)}m {int(seconds % 60)}s")
            except Exception:
                st.text("—")

    # Download link
    artifact_id = artifact.get("id", "")
    file_path = artifact.get("file_path")
    if file_path and artifact_id:
        st.caption(f"File: `{file_path}`")
