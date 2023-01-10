from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.status import HTTP_401_UNAUTHORIZED

from src.core.security import get_current_active_user
from src.schemas.user import UserOut
from src.db.repositories.base import BaseService
from src.schemas.job import JobCreate, JobOut, JobUpdate
from src.db.models.jobs import Job


class JobsService(BaseService[JobCreate, JobOut, JobUpdate]):
    def __init__(self):
        super().__init__(Job)

    async def create(self, obj: JobCreate, db: AsyncSession,
                     user: UserOut = Depends(get_current_active_user)) -> JobOut:
        obj_dict = obj.dict()
        obj_dict['user_id'] = user.id
        instance = self.model(**obj_dict)
        db.add(instance)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email is already registered")
        return instance

    async def update(self, pk: int, obj: JobCreate, db: AsyncSession, user: UserOut) -> JobOut:
        job = await self.get_one(pk)
        if job.user_id == user.id or user.is_superuser:
            return await super().update(pk, obj, db)
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized for this action")



def get_jobs_service() -> JobsService:
    return JobsService()
