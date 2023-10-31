from typing import List

from fastapi import Depends, UploadFile, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from . import time_tracking_route

from semant_annotation.authentication import get_current_user
from semant_annotation.db import get_async_session, crud_general, crud_time_tracking
from semant_annotation.schemas import base_objects
from semant_annotation.schemas.auth_objects import TokenData
from semant_annotation.db import model

from uuid import UUID
from datetime import datetime


# Get all time tracking entries for a user (admin only) or for the current user (user only).
# Can be filtered by from_time and to_time. If no filter is given, all entries are returned.
@time_tracking_route.get("/time_tracking", response_model=List[base_objects.TimeTrackingItem], tags=["Time Tracking"])
async def get_time_tracking(
        from_time: datetime = None,
        to_time: datetime = None,
        user_id: UUID = None,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    if not user_token.trusted_user or user_id is None:
        user_id = user_token.user_id
    results = await crud_time_tracking.get_user_time_tracking(db, user_id, from_time, to_time)
    return results


@time_tracking_route.get("/time_tracking/{time_tracking_id}", response_model=base_objects.TimeTrackingItem, tags=["Time Tracking"])
async def get_time_tracking_by_id(time_tracking_id: UUID,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    time_tracking_item = await crud_general.get(db, base_objects.TimeTrackingItem, model.TimeTrackingItem, time_tracking_id)
    if not user_token.trusted_user and time_tracking_item.user_id != user_token.user_id:
        raise HTTPException(status_code=403, detail="Can only access own time tracking entries.")
    return time_tracking_item


@time_tracking_route.post("/time_tracking", tags=["Time Tracking"])
async def new_time_tracking(time_tracking: base_objects.TimeTrackingItemNew,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    if not user_token.trusted_user and time_tracking.user_id != user_token.user_id:
        raise HTTPException(status_code=403, detail="Can only create own time tracking entries.")
    await crud_general.new(db, time_tracking, model.TimeTrackingItem)


@time_tracking_route.delete("/time_tracking/{time_tracking_id}", tags=["Time Tracking"])
async def delete_time_tracking(time_tracking_id: UUID,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    await crud_time_tracking.delete_user_time_tracking(db, user_token.user_id, time_tracking_id)
