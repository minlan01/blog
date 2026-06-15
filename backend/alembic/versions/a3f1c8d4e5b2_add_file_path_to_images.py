"""Add file_path column to images table

Revision ID: a3f1c8d4e5b2
Revises: 62dbd9b622d0
Create Date: 2026-05-22 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3f1c8d4e5b2'
down_revision: Union[str, None] = '62dbd9b622d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('images', sa.Column('file_path', sa.String(length=512), nullable=True))
    op.alter_column('images', 'data', existing_type=sa.LargeBinary(), nullable=True)


def downgrade() -> None:
    op.alter_column('images', 'data', existing_type=sa.LargeBinary(), nullable=False)
    op.drop_column('images', 'file_path')
