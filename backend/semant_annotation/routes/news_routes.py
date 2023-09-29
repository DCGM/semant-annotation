from typing import List

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from . import news_route

from semant_annotation.authentication import get_current_admin
from semant_annotation.db import get_async_session, crud_general
from semant_annotation.schemas import base_objects
from semant_annotation.schemas.auth_objects import TokenData
from semant_annotation.db import model


@news_route.get("/", response_model=List[base_objects.News], tags=["News"])
async def get_news(limit: int = 1000,
        db: AsyncSession = Depends(get_async_session)):
    return await crud_general.get_all(db, base_objects.News, model.News, limit=limit)


@news_route.post("/", tags=["News"])
async def new_news(news: base_objects.NewsUpdate,
                   user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.new(db, news, model.News)


@news_route.put("/", tags=["News"])
async def update_news(news: base_objects.News,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_general.update_obj(db, news, model.News)
