import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select, or_
from .database import DBError
from . import model
from semant_annotation.schemas import base_objects
from datetime import datetime, timedelta
from uuid import UUID
import random


def base_select_random_instance(task_id: UUID, available_result_count: int, time_delta: timedelta, random_number: int, greater_or_equal: bool):
    stmt = select(model.AnnotationTaskInstance).filter(model.AnnotationTaskInstance.annotation_task_id == task_id) \
        .filter(model.AnnotationTaskInstance.result_count == available_result_count) \
        .filter(or_(model.AnnotationTaskInstance.last_send_send_to_user == None,
                    model.AnnotationTaskInstance.last_send_send_to_user < datetime.now() - time_delta))
    if greater_or_equal:
        stmt = stmt.filter(model.AnnotationTaskInstance.random_number >= random_number)
    else:
        stmt = stmt.filter(model.AnnotationTaskInstance.random_number < random_number)
    return stmt.limit(1).with_for_update()


async def get_task_instance_random(db: AsyncSession, task_id: UUID, available_result_count: int):
    time_delta = timedelta(minutes=10)
    try:
        random_number = random.randint(0, model.max_random_number)
        stmt = base_select_random_instance(task_id, available_result_count, time_delta, random_number, True)
        result = await db.execute(stmt)
        db_task_instance = result.scalar_one_or_none()
        if not db_task_instance:
            stmt = base_select_random_instance(task_id, available_result_count, time_delta, random_number, False)
            result = await db.execute(stmt)
            db_task_instance = result.scalar_one_or_none()
        if not db_task_instance:
            return None
        db_task_instance.last_send_send_to_user = datetime.now()
        return base_objects.AnnotationTaskInstance.model_validate(db_task_instance)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching task instance from database.')
