"""initial observability tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-10 22:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '0005'
down_revision: Union[str, None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. metrics
    op.create_table(
        'metrics',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('unit', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_metrics_project_id'), 'metrics', ['project_id'], unique=False)

    # 2. metric_series
    op.create_table(
        'metric_series',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('metric_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('labels', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['metric_id'], ['metrics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_metric_series_metric_id'), 'metric_series', ['metric_id'], unique=False)
    op.create_index(op.f('ix_metric_series_timestamp'), 'metric_series', ['timestamp'], unique=False)

    # 3. log_entries
    op.create_table(
        'log_entries',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('service_name', sa.String(length=128), nullable=False),
        sa.Column('level', sa.String(length=64), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('labels', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_log_entries_project_id'), 'log_entries', ['project_id'], unique=False)
    op.create_index(op.f('ix_log_entries_service_name'), 'log_entries', ['service_name'], unique=False)
    op.create_index(op.f('ix_log_entries_level'), 'log_entries', ['level'], unique=False)
    op.create_index(op.f('ix_log_entries_timestamp'), 'log_entries', ['timestamp'], unique=False)

    # 4. traces
    op.create_table(
        'traces',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('trace_id', sa.String(length=128), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_traces_project_id'), 'traces', ['project_id'], unique=False)
    op.create_index(op.f('ix_traces_trace_id'), 'traces', ['trace_id'], unique=False)

    # 5. spans
    op.create_table(
        'spans',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('trace_uuid', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('span_id', sa.String(length=64), nullable=False),
        sa.Column('parent_span_id', sa.String(length=64), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(['trace_uuid'], ['traces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_spans_trace_uuid'), 'spans', ['trace_uuid'], unique=False)

    # 6. alert_rules
    op.create_table(
        'alert_rules',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.Column('severity', sa.String(length=64), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alert_rules_project_id'), 'alert_rules', ['project_id'], unique=False)

    # 7. alerts
    op.create_table(
        'alerts',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('rule_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('triggered_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['rule_id'], ['alert_rules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_rule_id'), 'alerts', ['rule_id'], unique=False)

    # 8. incidents
    op.create_table(
        'incidents',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('severity', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('assignee_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incidents_project_id'), 'incidents', ['project_id'], unique=False)

    # 9. incident_timelines
    op.create_table(
        'incident_timelines',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('incident_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_timelines_incident_id'), 'incident_timelines', ['incident_id'], unique=False)

    # 10. health_checks
    op.create_table(
        'health_checks',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('target', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=False),
        sa.Column('last_checked_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_health_checks_project_id'), 'health_checks', ['project_id'], unique=False)

    # 11. service_dependencies
    op.create_table(
        'service_dependencies',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('source_service', sa.String(length=128), nullable=False),
        sa.Column('target_service', sa.String(length=128), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_dependencies_project_id'), 'service_dependencies', ['project_id'], unique=False)

    # 12. slos
    op.create_table(
        'slos',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('target_percentage', sa.Float(), nullable=False),
        sa.Column('time_window_days', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_slos_project_id'), 'slos', ['project_id'], unique=False)

    # 13. slis
    op.create_table(
        'slis',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('slo_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('numerator', sa.Integer(), nullable=False),
        sa.Column('denominator', sa.Integer(), nullable=False),
        sa.Column('current_value', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['slo_id'], ['slos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_slis_slo_id'), 'slis', ['slo_id'], unique=False)

    # 14. notification_channels
    op.create_table(
        'notification_channels',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('config', sa.Text(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_channels_project_id'), 'notification_channels', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_table('notification_channels')
    op.drop_table('slis')
    op.drop_table('slos')
    op.drop_table('service_dependencies')
    op.drop_table('health_checks')
    op.drop_table('incident_timelines')
    op.drop_table('incidents')
    op.drop_table('alerts')
    op.drop_table('alert_rules')
    op.drop_table('spans')
    op.drop_table('traces')
    op.drop_table('log_entries')
    op.drop_table('metric_series')
    op.drop_table('metrics')
