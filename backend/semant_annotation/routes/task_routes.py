from typing import List

from fastapi import Depends, UploadFile, HTTPException
from fastapi.responses import FileResponse

from sqlalchemy.ext.asyncio import AsyncSession

from . import task_route

from semant_annotation.authentication import get_current_admin, get_current_user, add_user, get_password_hash
from semant_annotation.db import get_async_session, crud_general, crud_task
from semant_annotation.schemas import base_objects
from semant_annotation.schemas.auth_objects import TokenData
from semant_annotation.db import model
from semant_annotation.db.database import DBError
from uuid import UUID, uuid4
import os
import numpy as np
import cv2
import aiofiles
import aiofiles.os
import json
from semant_annotation.config import config


@task_route.get("/task", response_model=List[base_objects.AnnotationTask], tags=["Task"])
async def get_task(
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    return await crud_general.get_all(db, base_objects.AnnotationTask, model.AnnotationTask)


@task_route.get("/task/{task_id}", response_model=base_objects.AnnotationTask, tags=["Task"])
async def get_task_by_id(task_id: UUID,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    return await crud_general.get(db, base_objects.AnnotationTask, model.AnnotationTask, task_id)


@task_route.post("/task", tags=["Task"])
async def new_task(task: base_objects.AnnotationTaskUpdate,
                   user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.new(db, task, model.AnnotationTask)


@task_route.put("/task", tags=["Task"])
async def update_task(task: base_objects.AnnotationTaskUpdate,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.update_obj(db, task, model.AnnotationTask)


@task_route.delete("/task/{task_id}", tags=["Task"])
async def delete_task(task_id: UUID,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.delete_obj(db, task_id, model.AnnotationTask)


@task_route.post("/subtask", tags=["Task"])
async def new_subtask(subtask: base_objects.AnnotationSubtaskUpdate,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.new(db, subtask, model.AnnotationSubtask)


@task_route.put("/subtask", tags=["Task"])
async def update_subtask(subtask: base_objects.AnnotationSubtaskUpdate,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.update_obj(db, subtask, model.AnnotationSubtask)


@task_route.post("/task_instance", tags=["Task"])
async def new_task_instance(task_instance: base_objects.AnnotationTaskInstanceUpdate,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.new(db, task_instance, model.AnnotationTaskInstance)


@task_route.put("/task_instance", tags=["Task"])
async def update_task_instance(task_instance: base_objects.AnnotationTaskInstanceUpdate,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.update_obj(db, task_instance, model.AnnotationTaskInstance)


@task_route.get("/task_instance_random/{task_id}/{result_count_new}/{result_count_correction}", response_model=base_objects.AnnotationTaskInstance, tags=["Task"])
async def get_task_instance(task_id: UUID, result_count_new: int, result_count_correction: int,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    task = await crud_task.get_task_instance_random(db, task_id, result_count_new, result_count_correction)
    if task is None:
        raise HTTPException(status_code=404, detail="No task instance available.")
    return task


@task_route.get("/task_instance/{task_instance_id}", response_model=base_objects.AnnotationTaskInstance, tags=["Task"])
async def get_task_instance(task_instance_id: UUID,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    return await crud_general.get(db, base_objects.AnnotationTaskInstance, model.AnnotationTaskInstance, task_instance_id)


@task_route.post("/task_instance_result", tags=["Task"])
async def new_task_instance_result(task_instance_result: base_objects.AnnotationTaskResultUpdate,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    if not user_token.trusted_user:
        task_instance_result.user_id = user_token.user_id
    await crud_task.store_task_instance_result(db, task_instance_result)  # Needs to be special - can't use crud_general.new


@task_route.put("/task_instance_result", tags=["Task"])
async def update_task_instance_result(task_instance_result: base_objects.AnnotationTaskResultUpdate,
    user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.update_obj(db, task_instance_result, model.AnnotationTaskResult)


@task_route.post("/results", response_model=List[base_objects.AnnotationTaskResult], tags=["Task"])
async def get_task_instance_result(query: base_objects.AnnotationTaskResultQuery,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    return await crud_task.get_task_instance_results(db, query.annotation_task_id, query.user_id,
                                                     query.from_date, query.to_date)


@task_route.post("/result_times", response_model=List[base_objects.SimplifiedAnnotationTaskResult], tags=["Task"])
async def get_task_instance_result_times(query: base_objects.AnnotationTaskResultQuery,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    if not user_token.trusted_user and user_token.user_id != query.user_id:
        raise HTTPException(status_code=403, detail="You can only access your own statistics.")
    return await crud_task.get_task_instance_result_times(db, query.annotation_task_id, query.user_id,
                                                     query.from_date, query.to_date)

async def get_image_path(image_id: UUID, task_id: UUID, make_dir: bool = True):
    path = os.path.join(config.UPLOADED_IMAGES_FOLDER, str(task_id))
    if make_dir:
        await aiofiles.os.makedirs(path, exist_ok=True)
    return os.path.join(path, (str(image_id) + '.jpg'))


@task_route.get("/image/{task_id}/{image_id}", tags=["Task"])
async def get_image(task_id: UUID, image_id: UUID,
        user_token: TokenData = Depends(get_current_user)):
    path = await get_image_path(image_id=image_id, task_id=task_id, make_dir=False)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(path)


@task_route.post("/image/{task_id}", tags=["Task"])
async def upload_image(task_id: UUID, file: UploadFile,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    if 'image' not in file.content_type:
        raise HTTPException(status_code=400, detail=f"Unsuported file type - only images are supported.")

    try:
        raw_input = file.file.read()
        contents = np.asarray(bytearray(raw_input), dtype="uint8")
        image = cv2.imdecode(contents, -1)
        if image is None:
            raise HTTPException(status_code=400, detail="Failed to decode/open image.")

        instance_id = uuid4()

        write_path = await get_image_path(image_id=instance_id, task_id=task_id)
        async with aiofiles.open(write_path, mode='wb') as f:
            await f.write(raw_input)

        task_instance = base_objects.AnnotationTaskInstanceUpdate(
            id=instance_id, annotation_task_id=task_id, image=write_path, text='', active=True,
            instance_metadata=json.dumps({'type': 'image', 'original_filename': file.filename}))

        await crud_general.new(db, task_instance, model.AnnotationTaskInstance)

    except DBError as e:
        image_path = await get_image_path(image_id=instance_id, task_id=task_id)
        if os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(status_code=400, detail=f"Failed to upload image and add to dataset. {str(e)}")
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}


