"""initial kubernetes tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-10 22:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: Union[str, None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. clusters
    op.create_table(
        'clusters',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('slug', sa.String(length=128), nullable=False),
        sa.Column('environment_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column('encrypted_kubeconfig', sa.Text(), nullable=False),
        sa.Column('is_healthy', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['environment_id'], ['environments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_clusters_slug'), 'clusters', ['slug'], unique=True)

    # 2. namespaces
    op.create_table(
        'namespaces',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('cluster_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['cluster_id'], ['clusters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_namespaces_cluster_id'), 'namespaces', ['cluster_id'], unique=False)

    # 3. deployments
    op.create_table(
        'deployments',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('namespace_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('replicas', sa.Integer(), nullable=False),
        sa.Column('available_replicas', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['namespace_id'], ['namespaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deployments_namespace_id'), 'deployments', ['namespace_id'], unique=False)

    # 4. deployment_histories
    op.create_table(
        'deployment_histories',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('deployment_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['deployment_id'], ['deployments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deployment_histories_deployment_id'), 'deployment_histories', ['deployment_id'], unique=False)

    # 5. pods
    op.create_table(
        'pods',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('namespace_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('node_name', sa.String(length=128), nullable=True),
        sa.Column('restart_count', sa.Integer(), nullable=False),
        sa.Column('cpu_usage', sa.String(length=64), nullable=False),
        sa.Column('memory_usage', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['namespace_id'], ['namespaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pods_namespace_id'), 'pods', ['namespace_id'], unique=False)

    # 6. services
    op.create_table(
        'services',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('namespace_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('cluster_ip', sa.String(length=45), nullable=True),
        sa.Column('ports_config', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['namespace_id'], ['namespaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_services_namespace_id'), 'services', ['namespace_id'], unique=False)

    # 7. ingresses
    op.create_table(
        'ingresses',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('namespace_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('host', sa.String(length=255), nullable=True),
        sa.Column('path', sa.String(length=255), nullable=False),
        sa.Column('backend_service', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['namespace_id'], ['namespaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ingresses_namespace_id'), 'ingresses', ['namespace_id'], unique=False)

    # 8. configmaps
    op.create_table(
        'configmaps',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('namespace_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('data', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['namespace_id'], ['namespaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_configmaps_namespace_id'), 'configmaps', ['namespace_id'], unique=False)

    # 9. persistent_volumes
    op.create_table(
        'persistent_volumes',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('capacity', sa.String(length=64), nullable=False),
        sa.Column('access_modes', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. persistent_volume_claims
    op.create_table(
        'persistent_volume_claims',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('namespace_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('volume_name', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['namespace_id'], ['namespaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_persistent_volume_claims_namespace_id'), 'persistent_volume_claims', ['namespace_id'], unique=False)

    # 11. nodes
    op.create_table(
        'nodes',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('cluster_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('cpu_capacity', sa.String(length=64), nullable=False),
        sa.Column('memory_capacity', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['cluster_id'], ['clusters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_nodes_cluster_id'), 'nodes', ['cluster_id'], unique=False)

    # 12. helm_releases
    op.create_table(
        'helm_releases',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('namespace_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('chart_name', sa.String(length=128), nullable=False),
        sa.Column('version', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['namespace_id'], ['namespaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_helm_releases_namespace_id'), 'helm_releases', ['namespace_id'], unique=False)

    # 13. deployment_rollbacks
    op.create_table(
        'deployment_rollbacks',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('deployment_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('rollback_version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['deployment_id'], ['deployments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deployment_rollbacks_deployment_id'), 'deployment_rollbacks', ['deployment_id'], unique=False)


def downgrade() -> None:
    op.drop_table('deployment_rollbacks')
    op.drop_table('helm_releases')
    op.drop_table('nodes')
    op.drop_table('persistent_volume_claims')
    op.drop_table('persistent_volumes')
    op.drop_table('configmaps')
    op.drop_table('ingresses')
    op.drop_table('services')
    op.drop_table('pods')
    op.drop_table('deployment_histories')
    op.drop_table('deployments')
    op.drop_table('namespaces')
    op.drop_table('clusters')
