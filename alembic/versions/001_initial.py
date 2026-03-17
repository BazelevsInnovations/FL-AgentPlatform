"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-17
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("script_text", sa.Text(), server_default=""),
        sa.Column(
            "status",
            sa.Enum("draft", "in_progress", "completed", name="projectstatus"),
            server_default="draft",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "agent_configs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("agent_name", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("system_prompt", sa.Text(), server_default=""),
        sa.Column("model_id", sa.String(255), nullable=True),
        sa.Column("extra_params", sa.JSON(), server_default="{}"),
        sa.Column("is_default", sa.Boolean(), server_default="true"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Uuid(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("agent_name", sa.String(100), index=True, nullable=False),
        sa.Column("step", sa.Integer(), server_default="0"),
        sa.Column(
            "status",
            sa.Enum("pending", "running", "completed", "failed", name="runstatus"),
            server_default="pending",
        ),
        sa.Column("input_data", sa.JSON(), server_default="{}"),
        sa.Column("output_data", sa.JSON(), server_default="{}"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "artifacts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Uuid(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column(
            "agent_run_id",
            sa.Uuid(),
            sa.ForeignKey("agent_runs.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "artifact_type",
            sa.Enum("json", "text", "image", "video", "png", name="artifacttype"),
            nullable=False,
        ),
        sa.Column("content_text", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("artifacts")
    op.drop_table("agent_runs")
    op.drop_table("agent_configs")
    op.drop_table("projects")
    op.execute("DROP TYPE IF EXISTS artifacttype")
    op.execute("DROP TYPE IF EXISTS runstatus")
    op.execute("DROP TYPE IF EXISTS projectstatus")
