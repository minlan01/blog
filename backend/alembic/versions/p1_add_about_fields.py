"""Add about page editable fields to site_configs

Revision ID: p1_add_about
Revises: p1_drop_refresh_token
Create Date: 2026-07-30
"""
from alembic import op
import sqlalchemy as sa

revision = "p1_add_about"
down_revision = "p1_drop_refresh_token"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("site_configs", sa.Column("display_name", sa.String(120), nullable=True))
    op.add_column("site_configs", sa.Column("about_role", sa.String(255), nullable=True))
    op.add_column("site_configs", sa.Column("about_summary", sa.Text(), nullable=True))
    op.add_column("site_configs", sa.Column("about_me", sa.Text(), nullable=True))
    op.add_column("site_configs", sa.Column("about_project", sa.Text(), nullable=True))
    op.add_column("site_configs", sa.Column("project_highlights", sa.Text(), nullable=True))
    op.add_column("site_configs", sa.Column("tech_stack", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("site_configs", "tech_stack")
    op.drop_column("site_configs", "project_highlights")
    op.drop_column("site_configs", "about_project")
    op.drop_column("site_configs", "about_me")
    op.drop_column("site_configs", "about_summary")
    op.drop_column("site_configs", "about_role")
    op.drop_column("site_configs", "display_name")
