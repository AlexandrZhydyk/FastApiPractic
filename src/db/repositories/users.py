from fastapi import status
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED

from src.core.security import hash_password
from src.db.repositories.base import BaseService
from src.schemas.user import UserCreate, UserOut, UserUpdate
from src.db.models.users import User


class UsersService(BaseService[UserOut, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    async def create(self, obj: UserCreate, db: AsyncSession) -> UserOut:
        obj_dict = obj.dict()
        hashed_password = hash_password(obj_dict.get('password'))
        db_obj = self.model(
            email=obj_dict.get('email'),
            name=obj_dict.get('name'),
            is_company=obj_dict.get('is_company'),
            is_active=obj_dict.get('is_active'),
            hashed_password=hashed_password
        )
        db.add(db_obj)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email is already registered")
        return db_obj

    async def update(self, pk: int, obj: UserUpdate, db: AsyncSession, user: UserOut) -> UserUpdate:
        data_user = await self.get_one(pk, db)
        if data_user.id == user.id or user.is_superuser:
            return await super().update(pk, obj, db)
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized for this action")


def get_users_service() -> UsersService:
    return UsersService()

# import datetime
# from typing import List, Optional

# from schemas.user import UserCreate
# from db.models.users import User
# from .base import BaseRepository
#
#
# class UserRepository(BaseRepository):
#
#     async def create_user(user: UserCreate):
#         user = await User.create(**user.dict())
#         return user



    # async def get_user(id: str):
    #     user = await User.get(id)
    #     return user

    # async def get_all(self, limit: int = 100, skip: int = 0) -> List[User]:
    #     query = User.select().limit(limit).offset(skip)
    #     return await self.database.fetch_all(query=query)
    #
    # async def get_by_id(self, id: int) -> Optional[User]:
    #     query = User.select().where(User.c.id == id).first()
    #     user = await self.database.fetch_one(query=query)
    #     if user is None:
    #         return None
    #     return User.parse_obj(user)
    #
    # async def create(self, u: UserCreate) -> User:
    #     user = User(
    #         name=u.name,
    #         email=u.email,
    #         hashed_password=hash_password(u.password),
    #         is_company=u.is_company,
    #         created_at=datetime.datetime.utcnow(),
    #         updated_at=datetime.datetime.utcnow()
    #     )
    #     user_attr_dict = {**user.dict()}
    #     user_attr_dict.pop("id", None)
    #     query = User.insert().values(**user_attr_dict)
    #     user.id = await self.database.execute(query)
    #     return user
    #
    # async def update(self, id: int, u: UserCreate) -> User:
    #     user = User(
    #         name=u.name,
    #         email=u.email,
    #         hashed_password=hash_password(u.password),
    #         is_company=u.is_company,
    #         created_at=datetime.datetime.utcnow(),
    #         updated_at=datetime.datetime.utcnow()
    #     )
    #     user_attr_dict = {**user.dict()}
    #     user_attr_dict.pop("id", None)
    #     user_attr_dict.pop("created_at", None)
    #     query = users.update().where(users.c.id == id).values(**user_attr_dict)
    #     await self.database.execute(query)
    #     return user
    #
    # async def get_by_email(self, email: str) -> Optional[User]:
    #     query = users.select().where(users.c.email == id).first()
    #     user = await self.database.fetch_one(query=query)
    #     if user is None:
    #         return None
    #     return User.parse_obj(user)
