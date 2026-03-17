from __future__ import annotations

import json

import streamlit as st


def render_artifact(artifact: dict, api_base: str) -> None:
    art_type = artifact.get("artifact_type", "")
    name = artifact.get("name", "unknown")

    st.markdown(f"**{name}** ({art_type})")

    if art_type in ("json", "text"):
        content = artifact.get("content_text", "")
        if art_type == "json":
            try:
                parsed = json.loads(content)
                st.json(parsed)
            except json.JSONDecodeError:
                st.code(content)
        else:
            st.text(content)

    elif art_type in ("image", "png"):
        file_path = artifact.get("file_path", "")
        if file_path:
            try:
                st.image(file_path, caption=name)
            except Exception:
                artifact_id = artifact.get("id", "")
                project_id = artifact.get("project_id", "")
                st.markdown(f"[Download]({api_base}/api/v1/projects/{project_id}/artifacts/{artifact_id}/download)")

    elif art_type == "video":
        file_path = artifact.get("file_path", "")
        if file_path:
            try:
                st.video(file_path)
            except Exception:
                st.info(f"Video file: {file_path}")

    else:
        st.text(f"Unknown type: {art_type}")
