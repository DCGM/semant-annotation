import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select, or_, update
from .database import DBError
from . import model
from semant_annotation.schemas import base_objects
from datetime import datetime, timedelta
from uuid import UUID


async def get_user_time_tracking(db: AsyncSession, user_id: UUID, from_time: datetime, to_time: datetime) -> Union[base_objects.UserTimeTracking, None]:
    try:
        async with db.begin():
            query = select(model.UserTimeTracking).filter(model.UserTimeTracking.user_id == user_id)
            query = query.order_by(model.UserTimeTracking.start_time.asc())
            query = query.filter(model.UserTimeTracking.start_time.between(from_time, to_time))
            result = await db.execute(query)
            db_user_time_tracking = result.scalar_one_or_none()
            if db_user_time_tracking is None:
                return None
            return base_objects.UserTimeTracking.model_validate(db_user_time_tracking)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching user time tracking from database.')

