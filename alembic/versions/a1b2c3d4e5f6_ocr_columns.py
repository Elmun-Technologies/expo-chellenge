"""view_reports OCR tekshiruv ustunlari

Revision ID: a1b2c3d4e5f6
Revises: c14432b7a7ee
Create Date: 2026-09-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'c14432b7a7ee'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('view_reports', sa.Column('ocr_views', sa.Integer(), nullable=True))
    op.add_column('view_reports', sa.Column('ocr_handle', sa.String(length=64), nullable=True))
    op.add_column('view_reports', sa.Column('ocr_conf', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('view_reports', 'ocr_conf')
    op.drop_column('view_reports', 'ocr_handle')
    op.drop_column('view_reports', 'ocr_views')
