"""initial pipeline tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-10 22:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. pipelines
    op.create_table(
        'pipelines',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('slug', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipelines_slug'), 'pipelines', ['slug'], unique=False)
    op.create_index(op.f('ix_pipelines_project_id'), 'pipelines', ['project_id'], unique=False)

    # 2. pipeline_stages
    op.create_table(
        'pipeline_stages',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('pipeline_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('depends_on', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['pipeline_id'], ['pipelines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipeline_stages_pipeline_id'), 'pipeline_stages', ['pipeline_id'], unique=False)

    # 3. pipeline_jobs
    op.create_table(
        'pipeline_jobs',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('stage_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('needs', sa.String(length=255), nullable=True),
        sa.Column('runner_image', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['stage_id'], ['pipeline_stages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipeline_jobs_stage_id'), 'pipeline_jobs', ['stage_id'], unique=False)

    # 4. pipeline_steps
    op.create_table(
        'pipeline_steps',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('job_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('run_command', sa.Text(), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['pipeline_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipeline_steps_job_id'), 'pipeline_steps', ['job_id'], unique=False)

    # 5. pipeline_runs
    op.create_table(
        'pipeline_runs',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('pipeline_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('trigger_type', sa.String(length=64), nullable=False),
        sa.Column('commit_sha', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['pipeline_id'], ['pipelines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipeline_runs_pipeline_id'), 'pipeline_runs', ['pipeline_id'], unique=False)

    # 6. pipeline_run_stages
    op.create_table(
        'pipeline_run_stages',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('run_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('stage_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['run_id'], ['pipeline_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stage_id'], ['pipeline_stages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipeline_run_stages_run_id'), 'pipeline_run_stages', ['run_id'], unique=False)
    op.create_index(op.f('ix_pipeline_run_stages_stage_id'), 'pipeline_run_stages', ['stage_id'], unique=False)

    # 7. pipeline_run_jobs
    op.create_table(
        'pipeline_run_jobs',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('run_stage_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('job_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['run_stage_id'], ['pipeline_run_stages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['pipeline_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipeline_run_jobs_run_stage_id'), 'pipeline_run_jobs', ['run_stage_id'], unique=False)
    op.create_index(op.f('ix_pipeline_run_jobs_job_id'), 'pipeline_run_jobs', ['job_id'], unique=False)

    # 8. pipeline_run_logs
    op.create_table(
        'pipeline_run_logs',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('run_job_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['run_job_id'], ['pipeline_run_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipeline_run_logs_run_job_id'), 'pipeline_run_logs', ['run_job_id'], unique=False)

    # 9. pipeline_artifacts
    op.create_table(
        'pipeline_artifacts',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('run_job_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('path', sa.String(length=512), nullable=False),
        sa.Column('checksum', sa.String(length=64), nullable=False),
        sa.Column('size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('retention_days', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['run_job_id'], ['pipeline_run_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipeline_artifacts_run_job_id'), 'pipeline_artifacts', ['run_job_id'], unique=False)

    # 10. pipeline_variables
    op.create_table(
        'pipeline_variables',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('pipeline_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['pipeline_id'], ['pipelines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipeline_variables_pipeline_id'), 'pipeline_variables', ['pipeline_id'], unique=False)

    # 11. pipeline_secret_references
    op.create_table(
        'pipeline_secret_references',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('pipeline_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('secret_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['pipeline_id'], ['pipelines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipeline_secret_references_pipeline_id'), 'pipeline_secret_references', ['pipeline_id'], unique=False)

    # 12. execution_queues
    op.create_table(
        'execution_queues',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('run_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['run_id'], ['pipeline_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_execution_queues_run_id'), 'execution_queues', ['run_id'], unique=False)


def downgrade() -> None:
    op.drop_table('execution_queues')
    op.drop_table('pipeline_secret_references')
    op.drop_table('pipeline_variables')
    op.drop_table('pipeline_artifacts')
    op.drop_table('pipeline_run_logs')
    op.drop_table('pipeline_run_jobs')
    op.drop_table('pipeline_run_stages')
    op.drop_table('pipeline_runs')
    op.drop_table('pipeline_steps')
    op.drop_table('pipeline_jobs')
    op.drop_table('pipeline_stages')
    op.drop_table('pipelines')
