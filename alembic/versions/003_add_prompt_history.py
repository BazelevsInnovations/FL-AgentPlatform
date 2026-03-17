"""Add prompt_history table

Revision ID: 003
Revises: 002
Create Date: 2026-03-17
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prompt_history",
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
        sa.Column("agent_name", sa.String(100), index=True, nullable=False),
        sa.Column("system_prompt", sa.Text(), server_default=""),
        sa.Column("user_prompt", sa.Text(), server_default=""),
        sa.Column("model_id", sa.String(255), nullable=True),
        sa.Column("extra_params", sa.JSON(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("prompt_history")
