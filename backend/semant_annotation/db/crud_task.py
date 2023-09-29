import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select, func
from .database import DBError
from . import model
from semant_annotation.schemas import base_objects
from datetime import datetime, timedelta
from uuid import UUID


async def get_task_instance_random(db: AsyncSession, task_id: UUID, result_count: int):
    time_delta = timedelta(minutes=10)

    # Select oldest AnnotationTaskInstance with has not been sent to user for last time_delta minutes and atomicaly update value of last_send_send_to_user in databse.
    try:
        stmt = select(model.AnnotationTaskInstance).filter(model.AnnotationTaskInstance.task_id == task_id)\
            .filter(model.AnnotationTaskInstance.result_count == result_count) \
            .filter(model.AnnotationTaskInstance.last_send_send_to_user == None or model.AnnotationTaskInstance.last_send_send_to_user < datetime.now() - time_delta)\
            .order_by(model.AnnotationTaskInstance.created_date).limit(1).with_for_update()
        result = await db.execute(stmt)
        db_task_instance = result.scalar_one_or_none()
        if not db_task_instance:
            return None
        db_task_instance.last_send_send_to_user = datetime.now()
        await db.commit()
        return base_objects.AnnotationTaskInstance.model_validate(db_task_instance)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching task instance from database.')

