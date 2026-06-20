"""Add object storage fields to images

Revision ID: b4c2d9e8f1a0
Revises: a3f1c8d4e5b2
Create Date: 2026-06-20 22:15:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b4c2d9e8f1a0'
down_revision: Union[str, None] = 'a3f1c8d4e5b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('images', sa.Column('object_key', sa.String(length=512), nullable=True))
    op.add_column('images', sa.Column('storage_backend', sa.String(length=32), nullable=False, server_default='local'))
    op.add_column('images', sa.Column('media_type', sa.String(length=20), nullable=False, server_default='image'))


def downgrade() -> None:
    op.drop_column('images', 'media_type')
    op.drop_column('images', 'storage_backend')
    op.drop_column('images', 'object_key')
