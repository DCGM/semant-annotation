import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select, update
from .database import DBError
from . import model
from semant_annotation.schemas import base_objects

from typing import List


async def get_news(db: AsyncSession, limit: int = 1000) -> List[base_objects.News]:
    try:
        async with db.begin():
            db_news = await db.scalars(select(model.News).order_by(model.News.created_date.desc()).limit(limit))
            return [base_objects.News.model_validate(news) for news in db_news.all()]
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching news from database.')


async def new_news(db: AsyncSession, news: base_objects.NewsUpdate):
    try:
        async with db.begin():
            db_news = model.News(**news.model_dump())
            db.add(db_news)
            await db.commit()
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed fetching news from database.')


async def update_news(db: AsyncSession, news: base_objects.News):
    try:
        async with db.begin():
            stm = (update(model.News).where(model.News.id == news.id) \
                    .values(news.model_dump(exclude={'id'})))
            await db.execute(stm)
    except exc.SQLAlchemyError as e:
        logging.error(str(e))
        raise DBError(f'Failed updating news in database.')

