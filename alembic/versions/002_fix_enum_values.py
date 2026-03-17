"""Fix enum values: rename UPPERCASE to lowercase if needed

Revision ID: 002
Revises: 001
Create Date: 2026-03-17
"""
from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fix projectstatus enum if create_all created it with UPPERCASE values
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'DRAFT') THEN
                ALTER TYPE projectstatus RENAME VALUE 'DRAFT' TO 'draft';
                ALTER TYPE projectstatus RENAME VALUE 'IN_PROGRESS' TO 'in_progress';
                ALTER TYPE projectstatus RENAME VALUE 'COMPLETED' TO 'completed';
            END IF;
        END $$;
    """)

    # Fix runstatus enum
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'PENDING') THEN
                ALTER TYPE runstatus RENAME VALUE 'PENDING' TO 'pending';
                ALTER TYPE runstatus RENAME VALUE 'RUNNING' TO 'running';
                ALTER TYPE runstatus RENAME VALUE 'COMPLETED' TO 'completed';
                ALTER TYPE runstatus RENAME VALUE 'FAILED' TO 'failed';
            END IF;
        END $$;
    """)

    # Fix artifacttype enum
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'JSON') THEN
                ALTER TYPE artifacttype RENAME VALUE 'JSON' TO 'json';
                ALTER TYPE artifacttype RENAME VALUE 'TEXT' TO 'text';
                ALTER TYPE artifacttype RENAME VALUE 'IMAGE' TO 'image';
                ALTER TYPE artifacttype RENAME VALUE 'VIDEO' TO 'video';
                ALTER TYPE artifacttype RENAME VALUE 'PNG' TO 'png';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    pass
