import asyncio
from uuid import UUID, uuid4
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.connection import get_session
from src.models.auth import Organization, User
from src.models.project import Project, Environment, Repository
from src.models.pipeline import Pipeline
from src.models.kubernetes import Cluster
from src.models.observability import Incident, Metric
from src.models.ai import AIConversation

async def seed_demo_data():
    async for db in get_session():
        # 1. Fetch or create default Org
        org_query = select(Organization).where(Organization.name == "OpsPilot Demo Org")
        result = await db.execute(org_query)
        org = result.scalar_one_or_none()
        
        if not org:
            org = Organization(
                id=uuid4(),
                name="OpsPilot Demo Org",
                slug="opspilot-demo-org"
            )
            db.add(org)
            await db.commit()
            await db.refresh(org)
            print(f"Created Org: {org.name}")

        # 2. Create Project
        proj_query = select(Project).where(Project.name == "Core Ops Dashboard")
        result = await db.execute(proj_query)
        project = result.scalar_one_or_none()

        if not project:
            project = Project(
                id=uuid4(),
                organization_id=org.id,
                name="Core Ops Dashboard",
                slug="core-ops-dashboard"
            )
            db.add(project)
            await db.commit()
            await db.refresh(project)
            print(f"Created Project: {project.name}")

        # 3. Create Environment
        env_query = select(Environment).where(Environment.name == "Production")
        result = await db.execute(env_query)
        env = result.scalar_one_or_none()

        if not env:
            env = Environment(
                id=uuid4(),
                name="Production",
                slug="production"
            )
            db.add(env)
            await db.commit()
            await db.refresh(env)
            print(f"Created Environment: {env.name}")

        # 4. Create Git Provider
        from src.models.project import GitProvider
        provider_query = select(GitProvider).where(GitProvider.name == "Default GitHub")
        result = await db.execute(provider_query)
        git_provider = result.scalar_one_or_none()

        if not git_provider:
            git_provider = GitProvider(
                id=uuid4(),
                name="Default GitHub",
                provider_type="github",
                base_url="https://api.github.com"
            )
            db.add(git_provider)
            await db.commit()
            await db.refresh(git_provider)
            print(f"Created Git Provider: {git_provider.name}")

        # 5. Create Repository
        repo_query = select(Repository).where(Repository.name == "opspilot-service")
        result = await db.execute(repo_query)
        repo = result.scalar_one_or_none()

        if not repo:
            repo = Repository(
                id=uuid4(),
                organization_id=org.id,
                git_provider_id=git_provider.id,
                external_id="opspilot-service-ext-id",
                name="opspilot-service",
                full_name="opspilot/opspilot-service",
                clone_url="https://github.com/opspilot/opspilot-service.git",
                default_branch="main"
            )
            db.add(repo)
            await db.commit()
            print(f"Created Repository: {repo.name}")

        break  # End session loop

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
