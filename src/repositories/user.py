from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User

from .base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model=User)

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(self.model).where(self.model.username == username)
        )
        return result.scalar()

