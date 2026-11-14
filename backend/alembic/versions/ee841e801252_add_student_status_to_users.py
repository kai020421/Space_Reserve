"""add student status to users

Revision ID: ee841e801252
Revises: 5c60ac964c04
Create Date: 2026-11-11 15:21:44.274375

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee841e801252'
down_revision: Union[str, Sequence[str], None] = '5c60ac964c04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE public.users
        ADD COLUMN student_status TEXT
        CHECK (student_status IN ('enrolled', 'alumni'))
    """)


def downgrade() -> None:
    op.drop_column("users", "student_status", schema="public")