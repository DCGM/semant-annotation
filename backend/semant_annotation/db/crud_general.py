import logging
import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select, update, delete
from .database import DBError
from . import model
from semant_annotation.schemas import base_objects

from typing import List


async def get_all(db: AsyncSession, model_class: model.Base, table: model.Base, limit: int = 1000) -> List[model.Base]:
    try:
        async with db.begin():
            db_objects = await db.scalars(select(table).order_by(table.created_date.desc()).limit(limit))
            return [model_class.model_validate(obj) for obj in db_objects.all()]
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching objects from database.')


async def get(db: AsyncSession, model_class: model.Base, table: model.Base, id: UUID) -> model.Base:
    try:
        async with db.begin():
            db_obj = await db.scalar(select(table).where(table.id == id))
            return model_class.model_validate(db_obj)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching object from database.')


async def new(db: AsyncSession, obj: model.Base, table: model.Base):
    try:
        async with db.begin():
            db_obj = table(**obj.model_dump())
            db.add(db_obj)
            await db.commit()
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching object from database.')


async def update(db: AsyncSession, obj: model.Base, table: model.Base):
    try:
        async with db.begin():
            data = obj.model_dump(exclude={'id'})
            # add last_change with current timestamp
            data['last_change'] = datetime.now()

            stm = (update(table).where(table.id == obj.id) \
                    .values(data))
            await db.execute(stm)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed updating object in database.')


async def delete(db: AsyncSession, id: UUID, table: model.Base):
    try:
        async with db.begin():
            stm = (delete(table).where(table.id == id))
            await db.execute(stm)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed deleting object in database.')


