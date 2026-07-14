from typing import List, Optional
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.auth import Team, TeamMember

class TeamRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, team_id: UUID) -> Optional[Team]:
        return await self.db.get(Team, team_id)

    async def create(self, team: Team) -> Team:
        self.db.add(team)
        await self.db.commit()
        await self.db.refresh(team)
        return team

    async def update(self, team: Team) -> Team:
        self.db.add(team)
        await self.db.commit()
        await self.db.refresh(team)
        return team

    async def delete(self, team_id: UUID) -> bool:
        team = await self.db.get(Team, team_id)
        if team:
            await self.db.delete(team)
            await self.db.commit()
            return True
        return False

    async def list_for_org(self, org_id: UUID) -> List[Team]:
        query = select(Team).where(Team.organization_id == org_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def add_member(self, membership: TeamMember) -> TeamMember:
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        return membership
