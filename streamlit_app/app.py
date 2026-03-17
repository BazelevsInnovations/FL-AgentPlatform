import streamlit as st

st.set_page_config(
    page_title="FL-AgentPlatform",
    page_icon="🎬",
    layout="wide",
)

st.title("FL-AgentPlatform")
st.markdown("### Film Language Agent Platform")
st.markdown("""
Платформа AI-агентов для кинопроизводства.

**Навигация:**
- **Projects** — создание и управление проектами
- **Pipeline** — визуализация DAG pipeline агентов
- **Agent Detail** — просмотр входов/выходов, запуск агентов
- **Prompts** — редактирование системных промптов
- **Gallery** — галерея артефактов (JSON, изображения, видео)
- **Agent Settings** — настройка моделей для каждого агента

**API:** FastAPI сервер запускается отдельно: `uvicorn fl_platform.main:app --reload`
""")

import os

_default_api = os.getenv("API_BASE_URL", "http://localhost:8000")
API_BASE = st.sidebar.text_input("API URL", value=_default_api)
st.session_state["api_base"] = API_BASE
