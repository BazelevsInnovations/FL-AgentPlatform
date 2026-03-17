FROM python:3.11-slim AS base

WORKDIR /app

# System dependencies (graphviz for DAG visualization, matplotlib backend)
RUN apt-get update \
    && apt-get install -y --no-install-recommends graphviz \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .

# Copy application code
COPY streamlit_app/ streamlit_app/
COPY alembic/ alembic/
COPY alembic.ini .

RUN mkdir -p artifacts

EXPOSE 8000 8501
