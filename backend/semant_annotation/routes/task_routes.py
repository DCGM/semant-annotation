from typing import List

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from . import task_route

from semant_annotation.authentication import get_current_admin, get_current_user, add_user, get_password_hash
from semant_annotation.db import get_async_session, crud_general, crud_task
from semant_annotation.schemas import base_objects
from semant_annotation.schemas.auth_objects import TokenData
from semant_annotation.db import model


@task_route.get("/task", response_model=List[base_objects.AnnotationTask], tags=["Task"])
async def get_task(
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    return await crud_general.get_all(db, base_objects.AnnotationTask, model.AnnotationTask)


@task_route.post("/task", tags=["Task"])
async def new_task(task: base_objects.AnnotationTaskUpdate,
                   user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.new(db, task, model.AnnotationTask)


@task_route.put("/task", tags=["Task"])
async def update_task(task: base_objects.AnnotationTask,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.update(db, task, model.AnnotationTask)


@task_route.post("/subtask", tags=["Task"])
async def new_subtask(subtask: base_objects.AnnotationSubtaskUpdate,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.new(db, subtask, model.AnnotationSubtask)


@task_route.put("/subtask", tags=["Task"])
async def update_subtask(subtask: base_objects.AnnotationSubtask,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.update(db, subtask, model.AnnotationSubtask)


@task_route.post("/task_instance", tags=["Task"])
async def new_task_instance(task_instance: base_objects.AnnotationTaskInstanceUpdate,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.new(db, task_instance, model.AnnotationTaskInstance)


@task_route.put("/task_instance", tags=["Task"])
async def update_task_instance(task_instance: base_objects.AnnotationTaskInstanceUpdate,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.update(db, task_instance, model.AnnotationTaskInstance)


@task_route.get("/task_instance_random/:task_id/:result_count", response_model=List[base_objects.AnnotationTaskInstance], tags=["Task"])
async def get_task_instance(task_id: int, result_count: int,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    return await crud_task.get_task_instance_random(db, task_id, result_count)


@task_route.get("/task_instance/:task_id", response_model=List[base_objects.AnnotationTaskInstance], tags=["Task"])
async def get_task_instance(task_id: int,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    return await crud_task.get_task_instance(db, task_id)


@task_route.post("/task_instance_result", tags=["Task"])
async def new_task_instance_result(task_instance_result: base_objects.AnnotationTaskResultUpdate,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.new(db, task_instance_result, model.AnnotationTaskResult)


@task_route.put("/task_instance_result", tags=["Task"])
async def update_task_instance_result(task_instance_result: base_objects.AnnotationTaskResultUpdate,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.update(db, task_instance_result, model.AnnotationTaskResult)


