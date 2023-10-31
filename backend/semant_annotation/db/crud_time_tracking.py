import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select, or_, update
from .database import DBError
from . import model
from semant_annotation.schemas import base_objects
from datetime import datetime, timedelta
from uuid import UUID
from typing import List, Union


async def get_user_time_tracking(db: AsyncSession, user_id: UUID, from_time: datetime, to_time: datetime) -> Union[base_objects.TimeTrackingItem, None]:
    try:
        async with db.begin():
            query = select(model.TimeTrackingItem).filter(model.TimeTrackingItem.user_id == user_id)\
                .filter(model.TimeTrackingItem.deleted == False)
            if from_time is not None:
                query = query.filter(model.TimeTrackingItem.start_time >= from_time)
            if to_time is not None:
                query = query.filter(model.TimeTrackingItem.start_time <= to_time)
            query = query.order_by(model.TimeTrackingItem.start_time.desc())
            db_objects = await db.execute(query)

            return [base_objects.TimeTrackingItem.model_validate(x) for x in db_objects.scalars()]
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching user time tracking from database.')


async def delete_user_time_tracking(db: AsyncSession, user_id: UUID, time_trakcing_id: UUID):
    ''' Set delted flag to true on user time tracking with id time_trakcing_id. If user_id is specified, only delete if user_id matches.'''
    try:
        async with db.begin():
            query = update(model.TimeTrackingItem).where(model.TimeTrackingItem.id == time_trakcing_id)
            if user_id is not None:
                query = query.where(model.TimeTrackingItem.user_id == user_id)
            query = query.values({'deleted': True})
            await db.execute(query)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed deleting user time tracking from database.')

