"""initial governance tables

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-10 23:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '0007'
down_revision: Union[str, None] = '0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column('action', sa.String(length=128), nullable=False),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_project_id'), 'audit_logs', ['project_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)

    # 3. feature_flags
    op.create_table(
        'feature_flags',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feature_flags_project_id'), 'feature_flags', ['project_id'], unique=False)
    op.create_index(op.f('ix_feature_flags_key'), 'feature_flags', ['key'], unique=False)

    # 4. usage_statistics
    op.create_table(
        'usage_statistics',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('metric_name', sa.String(length=128), nullable=False),
        sa.Column('value', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_usage_statistics_project_id'), 'usage_statistics', ['project_id'], unique=False)
    op.create_index(op.f('ix_usage_statistics_metric_name'), 'usage_statistics', ['metric_name'], unique=False)
    op.create_index(op.f('ix_usage_statistics_timestamp'), 'usage_statistics', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_table('usage_statistics')
    op.drop_table('feature_flags')
    op.drop_table('audit_logs')
