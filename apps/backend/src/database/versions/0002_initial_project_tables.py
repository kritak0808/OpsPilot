"""initial project tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-10 21:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. projects
    op.create_table(
        'projects',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('organization_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('slug', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_slug'), 'projects', ['slug'], unique=False)
    op.create_index(op.f('ix_projects_organization_id'), 'projects', ['organization_id'], unique=False)

    # 2. project_members
    op.create_table(
        'project_members',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('role', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_members_project_id'), 'project_members', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_members_user_id'), 'project_members', ['user_id'], unique=False)

    # 3. applications
    op.create_table(
        'applications',
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
    op.create_index(op.f('ix_applications_slug'), 'applications', ['slug'], unique=False)
    op.create_index(op.f('ix_applications_project_id'), 'applications', ['project_id'], unique=False)

    # 4. application_variables
    op.create_table(
        'application_variables',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('application_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('is_secret', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_variables_application_id'), 'application_variables', ['application_id'], unique=False)

    # 5. environments
    op.create_table(
        'environments',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('slug', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_environments_slug'), 'environments', ['slug'], unique=True)

    # 6. deployment_targets
    op.create_table(
        'deployment_targets',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('environment_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('connection_details', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['environment_id'], ['environments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deployment_targets_environment_id'), 'deployment_targets', ['environment_id'], unique=False)

    # 7. git_providers
    op.create_table(
        'git_providers',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('provider_type', sa.String(length=64), nullable=False),
        sa.Column('base_url', sa.String(length=255), nullable=False),
        sa.Column('client_id', sa.String(length=255), nullable=True),
        sa.Column('client_secret', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. repositories
    op.create_table(
        'repositories',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('organization_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('application_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column('git_provider_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('clone_url', sa.String(length=512), nullable=False),
        sa.Column('default_branch', sa.String(length=64), nullable=False),
        sa.Column('webhook_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['git_provider_id'], ['git_providers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_repositories_organization_id'), 'repositories', ['organization_id'], unique=False)
    op.create_index(op.f('ix_repositories_application_id'), 'repositories', ['application_id'], unique=False)
    op.create_index(op.f('ix_repositories_git_provider_id'), 'repositories', ['git_provider_id'], unique=False)
    op.create_index(op.f('ix_repositories_external_id'), 'repositories', ['external_id'], unique=False)

    # 9. repository_credentials
    op.create_table(
        'repository_credentials',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('repository_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('provider_type', sa.String(length=64), nullable=False),
        sa.Column('encrypted_token', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_repository_credentials_repository_id'), 'repository_credentials', ['repository_id'], unique=False)

    # 10. webhooks
    op.create_table(
        'webhooks',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=512), nullable=False),
        sa.Column('secret', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhooks_external_id'), 'webhooks', ['external_id'], unique=False)


def downgrade() -> None:
    op.drop_table('webhooks')
    op.drop_table('repository_credentials')
    op.drop_table('repositories')
    op.drop_table('git_providers')
    op.drop_table('deployment_targets')
    op.drop_table('environments')
    op.drop_table('application_variables')
    op.drop_table('applications')
    op.drop_table('project_members')
    op.drop_table('projects')
