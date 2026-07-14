from typing import List, Optional
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.auth import Organization, OrganizationMember

class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        query = select(Organization).where(Organization.slug == slug)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, org_id: UUID) -> Optional[Organization]:
        return await self.db.get(Organization, org_id)

    async def create(self, org: Organization) -> Organization:
        self.db.add(org)
        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def update(self, org: Organization) -> Organization:
        self.db.add(org)
        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def list_for_user(self, user_id: UUID) -> List[Organization]:
        query = select(Organization).join(OrganizationMember).where(
            OrganizationMember.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def add_member(self, membership: OrganizationMember) -> OrganizationMember:
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def remove_member(self, org_id: UUID, user_id: UUID) -> bool:
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id
        )
        result = await self.db.execute(query)
        membership = result.scalar_one_or_none()
        if membership:
            await self.db.delete(membership)
            await self.db.commit()
            return True
        return False
        
    async def get_membership(self, org_id: UUID, user_id: UUID) -> Optional[OrganizationMember]:
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
