from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import Config

Base = declarative_base()

engine = create_async_engine(Config.DB_CONFIG, echo=True, future=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


# class AsyncDatabaseSession:
#     def __init__(self):
#         self._session = None
#         self._engine = None
#
#     def __getattr__(self, name):
#         return getattr(self._session, name)
#
#     def init(self):
#
#         self._engine = create_async_engine(
#             Config.DB_CONFIG,
#             future=True,
#             echo=True,
#         )
#         self._session = sessionmaker(
#             self._engine, expire_on_commit=False, class_=AsyncSession,
#             )()
#
#     async def create_all(self):
#         async with self._engine.begin() as conn:
#             await conn.run_sync(Base.metadata.create_all)
#
#
# db = AsyncDatabaseSession()


