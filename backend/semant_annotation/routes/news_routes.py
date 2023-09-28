from typing import List

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from . import news_route

from semant_annotation.authentication import get_current_admin
from semant_annotation.db import get_async_session, crud_news
from semant_annotation.schemas import base_objects
from semant_annotation.schemas.auth_objects import TokenData


@news_route.get("/", response_model=List[base_objects.News])
async def get_news(limit: int = 1000,
        db: AsyncSession = Depends(get_async_session)):
    return await crud_news.get_news(db, limit)


@news_route.post("/")
async def new_news(news: base_objects.NewsUpdate,
                   user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_news.new_news(db, news)


@news_route.put("/")
async def update_news(news: base_objects.News,
        user_token: TokenData = Depends(get_current_admin), db: AsyncSession = Depends(get_async_session)):
    await crud_news.update_news(db, news)
