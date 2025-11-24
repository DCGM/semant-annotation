import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select, or_, update, func
from .database import DBError
from . import model
from semant_annotation.schemas import base_objects
from datetime import datetime, timedelta
from uuid import UUID
import random



async def store_task_instance_result(db, task_instance_result: base_objects.AnnotationTaskResultUpdate):
    try:
        async with db.begin():
            # must update task instance - increment  result_count_new or result_count_correction based on result_type
            # result_type = task_instance_result.result_type
            # if result_type == base_objects.AnnotationResultType.NEW:
            #     stmt = update(model.AnnotationTaskInstance).where(model.AnnotationTaskInstance.id == task_instance_result.annotation_task_instance_id)
            #     stmt = stmt.values({'result_count_new': model.AnnotationTaskInstance.result_count_new + 1})
            #     await db.execute(stmt)
            # elif result_type == base_objects.AnnotationResultType.CORRECTION:
            #     stmt = update(model.AnnotationTaskInstance).where(model.AnnotationTaskInstance.id == task_instance_result.annotation_task_instance_id)
            #     stmt = stmt.values({'result_count_correction': model.AnnotationTaskInstance.result_count_correction + 1})
            #     await db.execute(stmt)
            stmt = update(model.AnnotationTaskInstance).where(model.AnnotationTaskInstance.id == task_instance_result.annotation_task_instance_id)
            stmt = stmt.values({'result_count_new': model.AnnotationTaskInstance.result_count_new + 1})
            await db.execute(stmt)

            db_task_instance_result = model.AnnotationTaskResult(**task_instance_result.model_dump())
            db.add(db_task_instance_result)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed storing task instance result in database.')


def base_select_random_instance(task_id: UUID, result_count_new: int, result_count_correction: int, time_delta: timedelta, random_number: int, greater_or_equal: bool) -> select:
    stmt = select(model.AnnotationTaskInstance).filter(model.AnnotationTaskInstance.annotation_task_id == task_id)
    if result_count_correction >= 0:
        stmt = stmt.filter(model.AnnotationTaskInstance.result_count_correction == result_count_correction)
    if result_count_new >= 0:
        stmt = stmt.filter(model.AnnotationTaskInstance.result_count_new == result_count_new)
    stmt = stmt.filter(or_(model.AnnotationTaskInstance.last_send_send_to_user == None,
                    model.AnnotationTaskInstance.last_send_send_to_user < datetime.now() - time_delta))
    if greater_or_equal:
        stmt = stmt.filter(model.AnnotationTaskInstance.random_number >= random_number)
    else:
        stmt = stmt.filter(model.AnnotationTaskInstance.random_number < random_number)
    return stmt.limit(1).with_for_update()


async def get_task_instance_random(db: AsyncSession, task_id: UUID, result_count_new: int, result_count_correction: int) -> base_objects.AnnotationTaskInstance:
    time_delta = timedelta(minutes=10)
    try:
        async with db.begin():
            random_number = random.randint(0, model.max_random_number)
            stmt = base_select_random_instance(task_id, result_count_new, result_count_correction, time_delta, random_number, True)
            result = await db.execute(stmt)
            db_task_instance = result.scalar_one_or_none()
            if not db_task_instance:
                stmt = base_select_random_instance(task_id, result_count_new, result_count_correction, time_delta, random_number, False)
                result = await db.execute(stmt)
                db_task_instance = result.scalar_one_or_none()
            if not db_task_instance:
                return None
            db_task_instance.last_send_send_to_user = datetime.now()
            return  base_objects.AnnotationTaskInstance.model_validate(db_task_instance)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching task instance from database.')


async def get_task_instance_results(db: AsyncSession, task_id: UUID, offset: int, page_size: int, user_id: UUID=None, from_date: datetime=None, 
                                    to_date: datetime=None) -> base_objects.AnnotationTaskResult:
    try:
        async with db.begin():
            stmt = select(model.AnnotationTaskResult).join(model.AnnotationTaskInstance)\
                .where(model.AnnotationTaskInstance.annotation_task_id == task_id)
            if user_id:
                stmt = stmt.where(model.AnnotationTaskResult.user_id == user_id)
            if from_date:
                stmt = stmt.where(model.AnnotationTaskResult.created_date >= from_date)
            if to_date:
                stmt = stmt.where(model.AnnotationTaskResult.created_date <= to_date)

            stmt = stmt.offset(offset).limit(page_size)
            result = await db.execute(stmt)
            db_task_instance_result = result.scalars().all()

            return [base_objects.AnnotationTaskResult.model_validate(db_task_instance_result) for db_task_instance_result in db_task_instance_result]
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching task instance result from database.')

async def get_task_instance_results_count(db: AsyncSession, task_id: UUID, user_id: UUID=None, from_date: datetime=None, 
                                    to_date: datetime=None) -> int:
    try:
        async with db.begin():
            stmt = select(func.count()).select_from(model.AnnotationTaskResult).join(model.AnnotationTaskInstance)\
                .where(model.AnnotationTaskInstance.annotation_task_id == task_id)
            if user_id:
                stmt = stmt.where(model.AnnotationTaskResult.user_id == user_id)
            if from_date:
                stmt = stmt.where(model.AnnotationTaskResult.created_date >= from_date)
            if to_date:
                stmt = stmt.where(model.AnnotationTaskResult.created_date <= to_date)

            result = await db.execute(stmt)
            count = result.scalar()

            return count
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching total count of task instance results from database.')

async def get_task_instance_result_times(db: AsyncSession, task_id: UUID = None, user_id: UUID=None, from_date: datetime=None,
                                    to_date: datetime=None) -> base_objects.SimplifiedAnnotationTaskResult:
    try:
        async with db.begin():
            stmt = select(model.AnnotationTaskResult.start_time,
                          model.AnnotationTaskResult.end_time,
                          model.AnnotationTaskResult.result_type,
                          model.AnnotationTaskResult.user_id)
            if task_id:
                stmt = stmt.join(model.AnnotationTaskInstance).where(model.AnnotationTaskInstance.annotation_task_id == task_id)
            if user_id:
                stmt = stmt.where(model.AnnotationTaskResult.user_id == user_id)
            if from_date:
                stmt = stmt.where(model.AnnotationTaskResult.created_date >= from_date)
            if to_date:
                stmt = stmt.where(model.AnnotationTaskResult.created_date <= to_date)
            result = await db.execute(stmt.distinct())
            db_task_instance_result = result.all()
            return [base_objects.SimplifiedAnnotationTaskResult.model_validate(db_task_instance_result) for db_task_instance_result in db_task_instance_result]
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching task instance result from database.')