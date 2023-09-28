from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from semant_annotation.config import config
from typing import AsyncGenerator

engine = None
async_session_maker = None


async def init_db() -> None:
    from . import Base
    local_engine = create_async_engine(config.SQLALCHEMY_DATABASE_URL)
    async with local_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await fill_db(local_engine)


# Dependency
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    global engine, async_session_maker
    if engine is None:
        engine = create_async_engine(config.SQLALCHEMY_DATABASE_URL, pool_size=20, max_overflow=60)
        async_session_maker = sessionmaker(engine, autocommit=False, autoflush=False, class_=AsyncSession)
    async with async_session_maker() as session:
        yield session


class DBError(Exception):
    pass


async def fill_db(local_engine) -> None:
    from semant_annotation.db import model
    from semant_annotation.authentication import add_user
    from semant_annotation.schemas import base_objects
    from uuid import uuid4
    import logging

    async_session_maker = sessionmaker(local_engine, autocommit=False, autoflush=False, class_=AsyncSession)
    session = async_session_maker()
    async with session.begin():
        result = await session.execute(select(model.User))
    if result.all():
        return

    admin_id = uuid4()
    await add_user(session,
                   base_objects.User(
                 id=admin_id, username=config.ADMIN_USERNAME, email="cosi@gdesi.com", full_name=config.ADMIN_USERNAME,
                 institution="FIT VUT", disabled=False, trusted=1), config.ADMIN_PASSWORD)

    logging.info('ALL INSERTED')
