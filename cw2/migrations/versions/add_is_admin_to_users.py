"""Add is_admin to users

Revision ID: add_is_admin
Revises: 7a2e94dec124
Create Date: 2025-12-31 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_is_admin'
down_revision = '7a2e94dec124'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_admin column to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='0'))


def downgrade():
    # Remove is_admin column from users table
    op.drop_column('users', 'is_admin')

