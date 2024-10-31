from typing import List

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from . import user_route
from fastapi import HTTPException
from uuid import UUID

from semant_annotation.authentication import get_current_admin, get_current_user, add_user, get_password_hash
from semant_annotation.db import get_async_session, DBError, crud_user
from semant_annotation.schemas import base_objects
from semant_annotation.schemas.auth_objects import TokenData


@user_route.post("", response_model=None, tags=["User"])
async def add_user_route(user: base_objects.UserWithPasswd,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    user_dict = user.model_dump(exclude={'password'})
    await add_user(db, base_objects.User(**user_dict), user.password)


@user_route.put("", response_model=None, tags=["User"])
async def update_user(user: base_objects.User,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    if not user_token.trusted_user:
        raise HTTPException(status_code=403, detail="Can't change user data.")
    await crud_user.update_user(db, user)


@user_route.post("/register_user", response_model=None, tags=["User"])
async def register_user(user: base_objects.UserWithPasswd,
        db: AsyncSession = Depends(get_async_session)):
    user_dict = user.model_dump(exclude={'password'})
    user_dict.trusted = False
    user_dict.disabled = False
    await add_user(db, base_objects.User(**user_dict), user.password)


@user_route.get("", response_model=List[base_objects.User], tags=["User"])
async def get_all_users(
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    return await crud_user.get_all_users(db)


@user_route.get("/find", response_model=List[base_objects.User], tags=["User"])
async def get_all_users(query: str, limit: int = 4,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    limit = max(min(limit, 6), 1)
    return await crud_user.find_users_by_name(db, query, limit)


@user_route.put("/password", response_model=None, tags=["User"])
async def update_password(password: str, user_id: UUID,
        user_token: TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    if user_token.user_id != user_id and not user_token.trusted_user:
        raise HTTPException(status_code=403, detail="Can't change password of other users.")
    await crud_user.update_password(db, user_id, get_password_hash(password))

