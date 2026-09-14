"""view_reports.review_msg_id — moderator reply orqali javob yozish

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('view_reports', sa.Column('review_msg_id', sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column('view_reports', 'review_msg_id')
