"""Add authentication profile fields required by the merged API.

Revision ID: f1a2b3c4d5e6
Revises: ee841e801252
"""
from alembic import op
import sqlalchemy as sa

revision = "f1a2b3c4d5e6"
down_revision = "ee841e801252"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("users", sa.Column("erp_id", sa.String(length=32), nullable=True), schema="public")
    op.add_column("users", sa.Column("enrollment_number", sa.String(length=32), nullable=True), schema="public")
    op.add_column("users", sa.Column("program", sa.String(length=80), nullable=True), schema="public")
    op.add_column("users", sa.Column("is_ta", sa.Boolean(), nullable=False, server_default=sa.false()), schema="public")
    op.add_column("users", sa.Column("department", sa.String(length=120), nullable=True), schema="public")
    op.add_column("users", sa.Column("represents", sa.Text(), nullable=False, server_default=""), schema="public")
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), schema="public")

def downgrade():
    op.drop_column("users", "is_active", schema="public")
    op.drop_column("users", "represents", schema="public")
    op.drop_column("users", "department", schema="public")
    op.drop_column("users", "is_ta", schema="public")
    op.drop_column("users", "program", schema="public")
    op.drop_column("users", "enrollment_number", schema="public")
    op.drop_column("users", "erp_id", schema="public")
