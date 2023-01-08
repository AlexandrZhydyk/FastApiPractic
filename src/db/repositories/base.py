from datetime import datetime

from fastapi import status
from typing import Generic, List, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from src.db.base import Base
from sqlalchemy.future import select


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, obj: CreateSchemaType, db: AsyncSession) -> ModelType:
        instance = self.model(**obj.dict())
        db.add(instance)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Incorrect value was entered")
        return instance

    async def get_all(self, db: AsyncSession) -> List[ModelType]:
        query = select(self.model)
        db_obj: List[ModelType] = await db.execute(query)
        instances = db_obj.scalars().all()
        if not instances:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no objects")
        return instances

    async def get_one(self, pk: int, db: AsyncSession) -> ModelType:
        query = select(self.model).where(self.model.id == pk)
        db_obj = await db.execute(query)
        instance = db_obj.scalar()
        if not instance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no object")
        return instance

    async def update(self, pk: int, obj: ModelType, db: AsyncSession) -> ModelType:
        obj_dict = obj.dict(exclude_none=True)
        obj_dict['updated_at'] = datetime.utcnow()
        query = update(self.model).where(self.model.id == pk).values(**obj_dict).returning(self.model)
        instance = await db.execute(query)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Incorrect value was entered")
        return instance.one_or_none()

    async def delete(self, pk: int, db: AsyncSession):
        query = delete(self.model).where(self.model.id == pk)
        await db.execute(query)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no object to delete")
        return True

